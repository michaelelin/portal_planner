import geometry
from geometry import Position
import planning.objects

class Drawable:
    def draw(self, canvas):
        pass

class Player(planning.objects.Player, Drawable):
    def draw(self, canvas):
        self._id = canvas.create_oval(self.x - 0.3, self.y - 0.3,
                                      self.x + 0.3, self.y + 0.3, fill='red')

class Entity(Drawable):
    @staticmethod
    def deserialize(obj):
        return ENTITY_TYPES[obj['type']].deserialize(obj)

class Portal(Entity, planning.objects.Portal):
    def __init__(self, pos1, pos2, name):
        self.pos1 = pos1
        self.pos2 = pos2

        x1, y1, x2, y2 = geometry.offset_line(*self.pos1, *self.pos2, -0.1)
        planning.objects.Portal.__init__(self, (x1 + x2) * 0.5, (y1 + y2) * 0.5, name)

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
    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.3, self.y - 0.3, self.x + 0.3, self.y + 0.3, fill='black')

    @staticmethod
    def deserialize(obj):
        return Cube(*obj['pos'])

class Button(planning.objects.Button, Position):
    def __init__(self, x, y):
        planning.objects.Button.__init__(self)
        Position.__init__(self, x, y)

    def draw(self, canvas):
        canvas.create_oval(self.x - 0.8, self.y - 0.8, self.x + 0.8, self.y + 0.8, fill='red')

    @staticmethod
    def deserialize(obj):
        return Button(*obj['pos'])

ENTITY_TYPES = {
    'portal1': Portal1,
    'portal2': Portal2,
    'cube': Cube,
    'button': Button
}
