import tkinter as tk

import geometry

class Wall:
    def __init__(self, pos1, pos2):
        self.x1, self.y1 = pos1
        self.x2, self.y2 = pos2

    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    def intersects(self, pos1, pos2):
        x3, y3 = pos1
        x4, y4 = pos2
        det = ((self.x1 - self.x2) * (y3 - y4)) - ((self.y1 - self.y2) * (x3 - x4))
        if det != 0:
            t = float(((self.x1 - x3) * (y3 - y4)) - ((self.y1 - y3) * (x3 - x4))) / det
            u = float(((self.x1 - self.x2) * (self.y1 - y3)) - ((self.y1 - self.y2) * (self.x1 - x3))) / -det
            return 0.0 <= t and t <= 1.0 and 0.0 <= u and u <= 1.0
        else:
            return False

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=2.0, capstyle=tk.ROUND)

    @staticmethod
    def deserialize(obj):
        wall_type = obj.get('type') or 'wall'
        wall_cls = WALL_TYPES[wall_type]

        vertices = obj['vertices']
        return [wall_cls(tuple(pos1), tuple(pos2)) for pos1, pos2 in zip(vertices, vertices[1:])]

class Door(Wall):
    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=3.0, fill="green")

class Grill(Wall):
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
