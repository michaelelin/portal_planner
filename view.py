import functools
import sys
import tkinter as tk

from level import Level

class LevelCanvas(tk.Canvas):
    def __init__(self, app, level, width=400, height=400):
        self.level = level
        self.width = width
        self.height = height
        tk.Canvas.__init__(self, app, width=width, height=height)
        self.bind('<Button-1>', self.handle_click)

        self._calculate_transform()
        self.path_lines = []

    def _calculate_transform(self):
        (x_min, y_min, x_max, y_max) = level.bounds()
        center_x = (x_min + x_max) * 0.5
        center_y = (y_min + y_max) * 0.5

        level_width = x_max - x_min
        level_height = y_max - y_min
        scale = min((self.width - 50) / level_width, (self.height - 50) / level_height)

        # A stack of Transforms
        self.transform = [
            Translate(-center_x, -center_y),
            Dilate(scale),
            Translate(self.width * 0.5, self.width * 0.5),
        ]
        self.inverse_transform = [t.inverse() for t in reversed(self.transform)]

    def transform_point(self, pos):
        return functools.reduce((lambda p, t: t.apply(p)), self.transform, pos)

    def preimage_point(self, pos):
        return functools.reduce((lambda p, t: t.apply(p)), self.inverse_transform, pos)

    def create_line(self, x1, y1, x2, y2, **options):
        x1_new, y1_new = self.transform_point((x1, y1))
        x2_new, y2_new = self.transform_point((x2, y2))
        return super().create_line(x1_new, y1_new, x2_new, y2_new, **options)

    def create_rectangle(self, x1, y1, x2, y2, **options):
        x1_new, y1_new = self.transform_point((x1, y1))
        x2_new, y2_new = self.transform_point((x2, y2))
        return super().create_rectangle(x1_new, y1_new, x2_new, y2_new, **options)

    def create_oval(self, x1, y1, x2, y2, **options):
        x1_new, y1_new = self.transform_point((x1, y1))
        x2_new, y2_new = self.transform_point((x2, y2))
        return super().create_oval(x1_new, y1_new, x2_new, y2_new, **options)

    def handle_click(self, event):
        path = self.level.navigation().search(self.level.start,
                                              self.preimage_point((event.x, event.y)))
        for line_id in self.path_lines:
            self.delete(line_id)
        self.path_lines = [self.create_line(node1.x, node1.y, node2.x, node2.y)
                           for node1, node2 in zip(path, path[1:])]

class Transform:
    def apply(self, pos):
        return pos

class Translate(Transform):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def apply(self, pos):
        x, y = pos
        return (x + self.dx, y + self.dy)

    def inverse(self):
        return Translate(-self.dx, -self.dy)

class Dilate(Transform):
    def __init__(self, scale):
        self.scale = scale

    def apply(self, pos):
        x, y = pos
        return (x * self.scale, y * self.scale)

    def inverse(self):
        return Dilate(1.0 / self.scale)


def handle_click(event):
    print(event)


if __name__ == '__main__':
    filename = sys.argv[1]
    level = Level.load(filename)

    root = tk.Tk()
    app = tk.Frame(root)
    canvas = LevelCanvas(app, level)
    canvas.pack()

    level.draw(canvas)
    # path = level.navigation().search((0.5, 3.5), (-0.5, -3.5))
    # for node1, node2 in zip(path, path[1:]):
        # canvas.create_line(node1.x, node1.y, node2.x, node2.y)

    app.pack()
    root.mainloop()
