# This is kind of messy, these should probably be more centralized
from .objects import *

class Predicate:
    def __init__(self, name, types):
        self.name = name
        self.types = types

    def __call__(self, *args):
        if len(self.types) != len(args):
            raise Exception('wrong number of arguments in predicate (%s %s)' %
                            (self.name, ' '.join([arg.name for arg in args])))

        for typ, obj in zip(self.types, args):
            if not isinstance(obj, typ):
                raise Exception('%s does not have type %s in predicate (%s %s)' %
                                (obj.name, typ.type(), self.name,
                                 ' '.join([arg.name for arg in args])))
        return PredicateInstance(self, args)

class PredicateInstance:
    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = args

    def serialize(self):
        return [self.predicate.name] + [arg.name for arg in self.args]

    def __hash__(self):
        return hash((self.predicate.name, self.args))

    def __eq__(self, other):
        return self.predicate == other.predicate and self.args == other.args

    def __repr__(self):
        return '(%s %s)' % (self.predicate.name, ' '.join([arg.name for arg in self.args]))

At = Predicate(
    'at', [Entity, Location]
)
Connected = Predicate(
    'connected', [Location, Location]
)
Carrying = Predicate(
    'carrying', [Player, Item]
)
ConnectorConnects = Predicate(
    'connector-connects', [Connector, Room, Room]
)
DoorRequires = Predicate(
    'door-requires', [Door, Button]
)
CanCreatePortal = Predicate(
    'can-create-portal', [Player, Portal]
)
CanCreatePortalAt = Predicate(
    'can-create-portal-at', [Location, Location]
)
