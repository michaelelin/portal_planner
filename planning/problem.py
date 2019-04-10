from .predicates import *
from .objects import *
from .planner import Planner

class Problem:
    def __init__(self, level):
        self.level = level
        self.player = level.player
        self.void = PORTAL_VOID
        self.objects = self._objects()

    def _objects(self):
        objects = ([self.player, self.void]
                  + self.level.navigation.rooms
                  + self.level.entities
                  + [w for w in self.level.walls if isinstance(w, Object)])
        return { obj.name: obj for obj in objects }

    def capability_predicates(self):
        capability_predicates = []
        for capability in self.level.capabilities:
            if capability == 'portal1':
                capability_predicates.append(CanCreatePortal(self.player, self.objects['portal1']))
            elif capability == 'portal2':
                capability_predicates.append(CanCreatePortal(self.player, self.objects['portal2']))
            else:
                raise Exception('Bad capability %s' % capability)
        return capability_predicates

    def location_predicates(self):
        return [At(obj, obj.get_location(self.level)) for obj in self.objects.values()
                if isinstance(obj, Entity)]

    def connection_predicates(self):
        connection_predicates = set()
        for node in self.level.navigation.nodes.values():
            for neighbor, wall, _ in node.neighbors:
                if neighbor and neighbor.room != node.room:
                    if isinstance(wall, Connector):
                        connection_predicates.add(ConnectorConnects(wall, node.room, neighbor.room))
                    else:
                        connection_predicates.add(Connected(node.room, neighbor.room))

        for obj in self.objects.values():
            if isinstance(obj, Button):
                loc = self.level.navigation.closest_node(obj).room
                connection_predicates.add(Connected(obj, loc))
                connection_predicates.add(Connected(loc, obj))

        return list(connection_predicates)

    def door_predicates(self):
        door_predicates = []
        for obj in self.objects.values():
            if isinstance(obj, Door):
                for trigger in obj.triggers:
                    door_predicates.append(DoorRequires(obj, trigger))
        return door_predicates

    def visibility_predicates(self):
        visibility_predicates = set()
        for room in self.level.navigation.rooms:
            for node in room.nodes:
                for other_room in self.level.navigation.rooms:
                    if node.visible_rooms[other_room]:
                        visibility_predicates.add(CanCreatePortalAt(room, other_room))
        return list(visibility_predicates)

    def initial_state(self):
        return (self.capability_predicates()
                + self.location_predicates()
                + self.connection_predicates()
                + self.door_predicates()
                + self.visibility_predicates())

    def goal_state(self):
        return At(self.player, self.level.navigation.closest_node(self.level.goal).room)

    def serialize(self):
        objects = sum([[name, '-', o.type()] for name, o in self.objects.items()],
                      [':objects'])
        init = [':init'] + [pred.serialize() for pred in self.initial_state()]
        goal = [':goal', self.goal_state().serialize()]
        return ['define', ['problem', self.level.name],
                [':domain', 'portal'],
                objects,
                init,
                goal]

    def solve(self):
        return Planner(self).plan()
