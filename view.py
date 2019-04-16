import functools
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from portal.geometry import Position
from portal.level import Level

FRAME_RATE = 60

class LevelCanvas(tk.Canvas):
    def __init__(self, app, level, width, height):
        self.level = level
        self.width = width
        self.height = height
        self.scale = None
        super().__init__(app, width=width, height=height)

        self.calculate_transform()
        self.path_lines = []
        self.bind('<Configure>', self.resize)

    def resize(self, event):
        self.width = event.width
        self.height = event.height
        self.calculate_transform()
        self.redraw()

    def set_scale(self, scale):
        self.scale = float(scale)
        self.calculate_transform()
        self.redraw()

    def calculate_transform(self):
        (x_min, y_min, x_max, y_max) = self.level.bounds
        center_x = (x_min + x_max) * 0.5
        center_y = (y_min + y_max) * 0.5

        level_width = x_max - x_min or 20
        level_height = y_max - y_min or 20
        scale = self.scale or min((self.width - 50) / level_width, (self.height - 50) / level_height)

        # A stack of Transforms
        self.transform = [
            Translate(-center_x, -center_y),
            Dilate(scale),
            Translate(self.width * 0.5, self.height * 0.5),
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

    def redraw(self):
        self.delete('all')
        self.level.draw(self)

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


class LevelView:
    def __init__(self, level, sequence=None, width=800, height=600):
        self.level = level
        self.sequence = sequence
        self.root = tk.Tk()
        self.root.title(level.name)
        self.app = tk.Frame(self.root)
        self.canvas = LevelCanvas(self.app, self.level, width=width, height=height)
        self.canvas.pack(side='top', fill=tk.BOTH, expand=True)

        if self.sequence:
            self.controls = tk.Frame(self.app)
            self.controls.pack(side='bottom')
            self.btn_play = ttk.Button(self.controls, text='Play', command=self.play)
            self.btn_play.pack()

        self.app.pack()

    def start(self):
        self.canvas.redraw()
        self.root.mainloop()

    def play(self):
        if self.sequence.actions is not None:
            self.root.after(int(1000 / FRAME_RATE), self.step)
        else:
            messagebox.showerror("Planning failed", "No solution found")

    def step(self):
        self.sequence.step()
        self.canvas.redraw()
        self.root.after(int(1000 / FRAME_RATE), self.step)

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        level = Level.load(f)

    LevelView(level).start()
