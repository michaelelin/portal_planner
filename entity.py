import geometry

class Entity:
    def draw(self, canvas):
        pass

    @staticmethod
    def deserialize(obj):
        return ENTITY_TYPES[obj['type']].deserialize(obj)


class Portal(Entity):
    def __init__(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2

    def draw(self, canvas):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        canvas.create_line(*geometry.offset_line(x1, y1, x2, y2, -0.1), width=3.0, fill=self.__class__.COLOR)

    @classmethod
    def deserialize(cls, obj):
        pos1 = tuple(obj['pos1'])
        pos2 = tuple(obj['pos2'])
        return cls(pos1, pos2)

class Portal1(Portal):
    COLOR = 'orange'

class Portal2(Portal):
    COLOR = 'blue'

class Cube:
    def __init__(self, pos):
        self.x, self.y = pos

    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.3, self.y - 0.3, self.x + 0.3, self.y + 0.3, fill='black')

    @staticmethod
    def deserialize(obj):
        pos = tuple(obj['pos'])
        return Cube(pos)

class Button:
    def __init__(self, pos):
        self.x, self.y = pos

    def draw(self, canvas):
        canvas.create_oval(self.x - 0.8, self.y - 0.8, self.x + 0.8, self.y + 0.8, fill='red')

    @staticmethod
    def deserialize(obj):
        pos = tuple(obj['pos'])
        return Button(pos)

ENTITY_TYPES = {
    'portal1': Portal1,
    'portal2': Portal2,
    'cube': Cube,
    'button': Button
}
