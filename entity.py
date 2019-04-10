import geometry
from geometry import Position
import planning.objects

class Drawable:
    def draw(self, canvas):
        pass

class Player(planning.objects.Player, Drawable):
    carrying = None
    on_button = None

    def draw(self, canvas):
        self._id = canvas.create_oval(self.x - 0.3, self.y - 0.3,
                                      self.x + 0.3, self.y + 0.3, fill='red')

    def _updated_position(self):
        super()._updated_position()
        if self.carrying:
            self.carrying.move_to(self)

    def step_on(self, btn):
        self.on_button = btn
        btn.add_object(self)

    def step_off(self, btn):
        self.on_button = None
        btn.remove_object(self)

    def pick_up(self, obj):
        if self.carrying is None:
            self.carrying = obj
            if self.on_button:
                self.on_button.remove_object(obj)
        else:
            raise Exception('already carrying an object')

    def put_down(self, obj):
        if self.carrying == obj:
            self.carrying = None
            if self.on_button:
                self.on_button.add_object(obj)
        else:
            raise Exception('not carrying that object')


class Entity(Drawable):
    @staticmethod
    def deserialize(obj):
        return ENTITY_TYPES[obj['type']].deserialize(obj)

class Portal(Entity, planning.objects.Portal):
    ORDER = 0
    def __init__(self, pos1, pos2, name):
        planning.objects.Object.__init__(self, name)
        self.set_endpoints(pos1, pos2)

    def reset(self):
        self.set_endpoints(None, None)

    def set_endpoints(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2
        if pos1 and pos2:
            x1, y1, x2, y2 = geometry.offset_line(*self.pos1, *self.pos2, -0.1)
            Position.__init__(self, (x1 + x2) * 0.5, (y1 + y2) * 0.5)

    def draw(self, canvas):
        if self.pos1 and self.pos2:
            x1, y1 = self.pos1
            x2, y2 = self.pos2
            canvas.create_line(*geometry.offset_line(x1, y1, x2, y2, -0.1), width=3.0, fill=self.__class__.COLOR)

    def get_location(self, level):
        if self.pos1 and self.pos2:
            return super().get_location(level)
        else:
            return planning.objects.PORTAL_VOID

    def create_on(self, segment, origin):
        intersection = segment.intersects(origin, segment.center())
        if intersection > 0:
            self.set_endpoints((segment.x2, segment.y2),
                               (segment.x1, segment.y1))
        else:
            self.set_endpoints((segment.x1, segment.y1),
                               (segment.x2, segment.y2))

    @classmethod
    def deserialize(cls, obj):
        pos1 = obj.get('pos1')
        pos2 = obj.get('pos2')
        if pos1 and pos2:
            return cls(tuple(pos1), tuple(pos2))
        else:
            return cls(None, None)

class Portal1(Portal):
    def __init__(self, pos1, pos2):
        super().__init__(pos1, pos2, "portal1")

    COLOR = 'orange'

class Portal2(Portal):
    def __init__(self, pos1, pos2):
        super().__init__(pos1, pos2, "portal2")

    COLOR = 'blue'

class Cube(Entity, planning.objects.Cube):
    ORDER = 2
    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.3, self.y - 0.3, self.x + 0.3, self.y + 0.3, fill='black')

    @staticmethod
    def deserialize(obj):
        return Cube(*obj['pos'])

class Button(planning.objects.Button, Position):
    ORDER = 1
    DRAW_RADIUS = 0.8
    def __init__(self, x, y):
        planning.objects.Button.__init__(self)
        Position.__init__(self, x, y)
        self.objects = set()

    def draw(self, canvas):
        if self.is_active():
            fill = 'dark red'
        else:
            fill = 'red'
        canvas.create_oval(self.x - Button.DRAW_RADIUS, self.y - Button.DRAW_RADIUS,
                           self.x + Button.DRAW_RADIUS, self.y + Button.DRAW_RADIUS,
                           fill=fill)

    def add_object(self, obj):
        self.objects.add(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def is_active(self):
        return bool(self.objects)

    @staticmethod
    def deserialize(obj):
        return Button(*obj['pos'])

ENTITY_TYPES = {
    'portal1': Portal1,
    'portal2': Portal2,
    'cube': Cube,
    'button': Button
}
