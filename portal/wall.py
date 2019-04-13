import math
import tkinter as tk

from portal import geometry
from portal.geometry import Position, Segment
from portal.planning import objects

class WallSegment(Segment):
    def __init__(self, pos1, pos2, parent=None):
        super().__init__(pos1, pos2)
        self.parent = parent

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

class Wall(WallSegment):
    def __init__(self, pos1, pos2):
        super().__init__(pos1, pos2)
        self._segment()

    def _segment(self):
        num_segments = round(Position(self.x1, self.y1).distance(Position(self.x2, self.y2)))
        self.segments = []
        for i in range(num_segments):
            self.segments.append(WallSegment((self.x1 + (self.x2 - self.x1) * (i / num_segments),
                                              self.y1 + (self.y2 - self.y1) * (i / num_segments)),
                                             (self.x1 + (self.x2 - self.x1) * ((i+1) / num_segments),
                                              self.y1 + (self.y2 - self.y1) * ((i+1) / num_segments)),
                                             self))

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, capstyle=tk.ROUND)


class Door(WallSegment, objects.Door):
    def __init__(self, pos1, pos2, triggers):
        WallSegment.__init__(self, pos1, pos2)
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

class Grill(WallSegment, objects.Grill):
    def __init__(self, pos1, pos2):
        WallSegment.__init__(self, pos1, pos2)
        objects.Grill.__init__(self)

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, fill="light blue")

class Ledge(WallSegment):
    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, capstyle=tk.ROUND)
        offset = self.offset(-0.2)
        canvas.create_line(offset.x1, offset.y1, offset.x2, offset.y2,
                           width=1.0,
                           dash=(4, 4))



WALL_TYPES = {
    'wall': Wall,
    'door': Door,
    'grill': Grill,
    'ledge': Ledge
}
