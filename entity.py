import geometry
import planning.objects

class Entity:
    def draw(self, canvas):
        pass

    @staticmethod
    def deserialize(obj):
        return ENTITY_TYPES[obj['type']].deserialize(obj)


class Portal(Entity, planning.objects.Portal):
    def __init__(self, pos1, pos2, name):
        planning.objects.Portal.__init__(self, name)
        self.pos1 = pos1
        self.pos2 = pos2

        x1, y1, x2, y2 = geometry.offset_line(*self.pos1, *self.pos2, -0.1)
        self.x = (x1 + x2) * 0.5
        self.y = (y1 + y2) * 0.5

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
    def __init__(self, pos1, pos2):
        super().__init__(pos1, pos2, "portal1")

    COLOR = 'orange'

class Portal2(Portal):
    def __init__(self, pos1, pos2):
        super().__init__(pos1, pos2, "portal2")

    COLOR = 'blue'

class Cube(Entity, planning.objects.Cube):
    def __init__(self, pos):
        planning.objects.Cube.__init__(self)
        self.x, self.y = pos

    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.3, self.y - 0.3, self.x + 0.3, self.y + 0.3, fill='black')

    @staticmethod
    def deserialize(obj):
        pos = tuple(obj['pos'])
        return Cube(pos)

class Button(planning.objects.Button):
    def __init__(self, pos):
        super().__init__()
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
