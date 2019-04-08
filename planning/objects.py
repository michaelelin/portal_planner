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

    def __eq__(self, other):
        return self.name == other.name

class Location(Object):
    pass

class Entity(Object):
    def get_location(self, level):
        raise Exception('get_location not implemented for %s' % self)

    def get_location(self, level):
        return level.navigation.closest_node((self.x, self.y)).room

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

class Player(Entity):
    def __init__(self, pos):
        super().__init__()
        self.x, self.y = pos

class Item(Movable):
    pass

class Cube(Item):
    pass
