import tkinter as tk

import geometry
import planning.objects

class Wall:
    def __init__(self, pos1, pos2):
        self.x1, self.y1 = pos1
        self.x2, self.y2 = pos2

    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    # Returns: 0 if no intersection
    #          1 if positive intersection
    #         -1 if negative intersection
    def intersects(self, pos1, pos2):
        x3, y3 = pos1
        x4, y4 = pos2
        det = ((self.x1 - self.x2) * (y3 - y4)) - ((self.y1 - self.y2) * (x3 - x4))
        if det != 0:
            t = float(((self.x1 - x3) * (y3 - y4)) - ((self.y1 - y3) * (x3 - x4))) / det
            u = float(((self.x1 - self.x2) * (self.y1 - y3)) - ((self.y1 - self.y2) * (self.x1 - x3))) / -det
            if 0.0 <= t and t <= 1.0 and 0.0 <= u and u <= 1.0:
                if det > 0:
                    return 1
                else:
                    return -1
        return 0

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, capstyle=tk.ROUND)

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


class Door(Wall, planning.objects.Door):
    def __init__(self, pos1, pos2, triggers):
        Wall.__init__(self, pos1, pos2)
        planning.objects.Door.__init__(self)
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

class Grill(Wall, planning.objects.Grill):
    def __init__(self, pos1, pos2):
        Wall.__init__(self, pos1, pos2)
        planning.objects.Grill.__init__(self)

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, fill="light blue")

class Ledge(Wall):
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_line(*geometry.offset_line(self.x1, self.y1, self.x2, self.y2, -0.2),
                           width=1.0,
                           dash=(4, 4))



WALL_TYPES = {
    'wall': Wall,
    'door': Door,
    'grill': Grill,
    'ledge': Ledge
}
