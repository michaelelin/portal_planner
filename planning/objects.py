from geometry import Position

class Object:
    _object_counter = 0

    def __init__(self, name=None):
        if name:
            self.name = name
        else:
            self.name = '%s%d' % (self.type(), self.__class__._object_counter)
            self.__class__._object_counter += 1

    @classmethod
    def type(cls):
        return cls.__name__.lower()

    def __hash__(self):
        return hash(self.name)

class Location(Object):
    pass

class Entity(Object, Position):
    def __init__(self, x, y, name=None):
        Position.__init__(self, x, y)
        Object.__init__(self, name)

    def get_location(self, level):
        return level.navigation.closest_node(self).room

class Connector(Object):
    pass

class Button(Location):
    pass

class Room(Location):
    pass

class Void(Location):
    pass

class Movable(Entity):
    pass

class Portal(Entity):
    pass

class Door(Connector):
    pass

class Grill(Connector):
    pass

class Player(Movable):
    pass

class Item(Movable):
    pass

class Cube(Item):
    pass

PORTAL_VOID = Void('portal-void')
