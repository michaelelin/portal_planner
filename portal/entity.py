import colors
from portal.geometry import Position, Segment
from portal.planning import objects

class Drawable:
    def draw(self, canvas):
        pass

class Player(objects.Player, Drawable):
    carrying = None
    on_button = None

    def draw(self, canvas):
        canvas.create_oval(self.x - 0.3, self.y - 0.3,
                           self.x + 0.3, self.y + 0.3, fill=colors.PLAYER)

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
    def serialize(obj):
        raise NotImplementedError

    @staticmethod
    def deserialize(obj):
        return ENTITY_TYPES[obj['type']].deserialize(obj)


class Portal(Entity, objects.Portal):
    ORDER = 3
    SPEED = 0.2
    EPSILON = 0.01
    PROJECTILE_SIZE = 1
    def __init__(self, pos1, pos2, name):
        objects.Object.__init__(self, name)
        self.set_endpoints(pos1, pos2)
        self.color = colors.PORTAL1 if name == 'portal1' else colors.PORTAL2
        self.target = None

    def reset(self):
        self.set_endpoints(None, None)

    def set_endpoints(self, pos1, pos2):
        self.pos1 = pos1.pos() if isinstance(pos1, Position) else pos1
        self.pos2 = pos2.pos() if isinstance(pos2, Position) else pos2
        if pos1 and pos2:
            offset = Segment(self.pos1, self.pos2).offset(-0.1)
            self.x, self.y = offset.center().pos()
        else:
            self.x = None
            self.y = None
        self.target = None

    def draw(self, canvas):
        if self.pos1 and self.pos2:
            x1, y1 = self.pos1
            x2, y2 = self.pos2
            offset = Segment(self.pos1, self.pos2).offset(-0.1)
            canvas.create_line(offset.x1, offset.y1, offset.x2, offset.y2,
                               width=3.0,
                               fill=self.color)
        elif self.x is not None and self.y is not None and self.target:
            distance = self.distance(self.target)
            dx = (self.target.x - self.x) * (self.PROJECTILE_SIZE / distance)
            dy = (self.target.y - self.y) * (self.PROJECTILE_SIZE / distance)
            canvas.create_line(self.x - dx, self.y - dy, self.x, self.y,
                               width=3.0,
                               fill=self.color)

    def move_toward(self, target, speed):
        super().move_toward(target, speed)
        self.target = target

    def get_location(self, level):
        if self.pos1 and self.pos2:
            return super().get_location(level)
        else:
            return objects.PORTAL_VOID

    def create_on(self, segment, origin):
        intersection = segment.intersects(origin, segment.center())
        if intersection > 0:
            self.set_endpoints((segment.x2, segment.y2),
                               (segment.x1, segment.y1))
        else:
            self.set_endpoints((segment.x1, segment.y1),
                               (segment.x2, segment.y2))

    def serialize(self):
        s = { 'type': self.name }
        if self.pos1 and self.pos:
            s['pos1'] = self.pos1
            s['pos2'] = self.pos2
        return s

    @staticmethod
    def deserialize(obj):
        pos1 = obj.get('pos1')
        pos2 = obj.get('pos2')
        name = obj['type']
        if pos1 and pos2:
            return Portal(tuple(pos1), tuple(pos2), name)
        else:
            return Portal(None, None, name)

class Cube(Entity, objects.Cube):
    ORDER = 2
    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.3, self.y - 0.3, self.x + 0.3, self.y + 0.3,
                                fill=colors.CUBE)

    def serialize(self):
        return { 'type': 'cube', 'pos': self.pos() }

    @staticmethod
    def deserialize(obj):
        return Cube(*obj['pos'])

class Button(objects.Button, Position):
    ORDER = 1
    DRAW_RADIUS = 0.8
    def __init__(self, x, y, name=None):
        objects.Button.__init__(self, name)
        Position.__init__(self, x, y)
        self.objects = set()

    def draw(self, canvas):
        if self.is_active():
            fill = colors.BUTTON_ACTIVE
        else:
            fill = colors.BUTTON
        canvas.create_oval(self.x - Button.DRAW_RADIUS, self.y - Button.DRAW_RADIUS,
                           self.x + Button.DRAW_RADIUS, self.y + Button.DRAW_RADIUS,
                           fill=fill)

    def add_object(self, obj):
        self.objects.add(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def is_active(self):
        return bool(self.objects)

    def serialize(self):
        return { 'type': 'button', 'id': self.name, 'pos': self.pos() }

    @staticmethod
    def deserialize(obj):
        return Button(*obj['pos'], obj.get('id'))

ENTITY_TYPES = {
    'portal1': Portal,
    'portal2': Portal,
    'cube': Cube,
    'button': Button
}
