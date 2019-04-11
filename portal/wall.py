import tkinter as tk

from portal import geometry
from portal.geometry import Position
from portal.planning import objects

class Segment:
    def __init__(self, pos1, pos2, parent=None):
        self.x1, self.y1 = pos1
        self.x2, self.y2 = pos2
        self.parent = parent
        self.x_min = min(self.x1, self.x2)
        self.x_max = max(self.x1, self.x2)
        self.y_min = min(self.y1, self.y2)
        self.y_max = max(self.y1, self.y2)

    def center(self):
        return Position((self.x1 + self.x2) * 0.5, (self.y1 + self.y2) * 0.5)

    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    # Returns: 0 if no intersection
    #          1 if positive intersection
    #         -1 if negative intersection
    def intersects(self, pos1, pos2):
        if ((pos1.x < self.x_min and pos2.x < self.x_min)
                or (pos1.x > self.x_max and pos2.x > self.x_max)
                or (pos1.y < self.y_min and pos2.y < self.y_min)
                or (pos1.y > self.y_max and pos2.y > self.y_max)):
            return 0

        det = ((self.x1 - self.x2) * (pos1.y - pos2.y)) - ((self.y1 - self.y2) * (pos1.x - pos2.x))
        if det != 0:
            t = float(((self.x1 - pos1.x) * (pos1.y - pos2.y)) - ((self.y1 - pos1.y) * (pos1.x - pos2.x))) / det
            u = float(((self.x1 - self.x2) * (self.y1 - pos1.y)) - ((self.y1 - self.y2) * (self.x1 - pos1.x))) / -det
            if 0.0 <= t and t <= 1.0 and 0.0 <= u and u <= 1.0:
                if det > 0:
                    return 1
                else:
                    return -1
        return 0

    @staticmethod
    def deserialize(obj, entities):
        wall_type = obj.pop('type', 'wall')
        wall_cls = WALL_TYPES[wall_type]

        vertices = obj.pop('vertices')

        wall_cls.translate_properties(obj, entities)
        return [wall_cls(tuple(pos1), tuple(pos2), **obj) for pos1, pos2 in zip(vertices, vertices[1:])]

    @staticmethod
    def translate_properties(props, entities):
        pass

class Wall(Segment):
    def __init__(self, pos1, pos2):
        super().__init__(pos1, pos2)
        self._segment()

    def _segment(self):
        num_segments = round(Position(self.x1, self.y1).distance(Position(self.x2, self.y2)))
        self.segments = []
        for i in range(num_segments):
            self.segments.append(Segment((self.x1 + (self.x2 - self.x1) * (i / num_segments),
                                          self.y1 + (self.y2 - self.y1) * (i / num_segments)),
                                         (self.x1 + (self.x2 - self.x1) * ((i+1) / num_segments),
                                          self.y1 + (self.y2 - self.y1) * ((i+1) / num_segments)),
                                         self))

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, capstyle=tk.ROUND)


class Door(Segment, objects.Door):
    def __init__(self, pos1, pos2, triggers):
        Segment.__init__(self, pos1, pos2)
        objects.Door.__init__(self)
        self.triggers = triggers

    def is_open(self):
        for trigger in self.triggers:
            if not trigger.is_active():
                return False
        return True

    def draw(self, canvas):
        if not self.is_open():
            canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=3.0, fill="green")

    @staticmethod
    def translate_properties(props, entities):
        props['triggers'] = [entities[t] for t in props['triggers']]

class Grill(Segment, objects.Grill):
    def __init__(self, pos1, pos2):
        Segment.__init__(self, pos1, pos2)
        objects.Grill.__init__(self)

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, fill="light blue")

class Ledge(Segment):
    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, capstyle=tk.ROUND)
        canvas.create_line(*geometry.offset_line(self.x1, self.y1, self.x2, self.y2, -0.2),
                           width=1.0,
                           dash=(4, 4))



WALL_TYPES = {
    'wall': Wall,
    'door': Door,
    'grill': Grill,
    'ledge': Ledge
}
