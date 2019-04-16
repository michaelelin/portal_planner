import math
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

import colors
import tools
from view import LevelCanvas, LevelView
from portal.animate import ActionSequence
from portal.level import Level

class EditorCanvas(LevelCanvas):
    def draw_grid(self):
        x0, y0 = self.preimage_point((0, 0))
        x1, y1 = self.preimage_point((self.width, self.height))
        x0 = math.floor(x0)
        y0 = math.floor(y0)
        x1 = math.ceil(x1)
        y1 = math.ceil(y1)
        for y in range(y0, y1 + 1):
            self.create_line(x0, y, x1, y, fill=colors.GRID)
        for x in range(x0, x1 + 1):
            self.create_line(x, y0, x, y1, fill=colors.GRID)

    def redraw(self):
        self.delete('all')
        self.draw_grid()
        self.level.draw(self)


class ControlPanel(ttk.Frame):
    CAPABILITIES = [('portal1', 'Create orange portal'),
                    ('portal2', 'Create blue portal')]
    def __init__(self, app, canvas, width):
        style = ttk.Style()
        style.theme_use('aqua')

        self.width = width
        super().__init__(app, width=width,
                         borderwidth=2,
                         relief=tk.SUNKEN,
                         padding=(6,6,6,6))

        self.canvas = canvas
        self.level = canvas.level
        self._setup_scale()
        self._setup_capabilities()
        self._setup_tools()
        ttk.Button(self, text='Run', command=self._run).pack(side='bottom')
        ttk.Button(self, text='Save', command=self._save).pack(side='bottom')

    def _setup_scale(self):
        self.scale_frame = ttk.Frame(self, width=self.width)

        ttk.Label(self.scale_frame, text='Zoom:').pack(side='left')

        self.scale = ttk.Scale(self.scale_frame, from_=10, to=100,
                              orient=tk.HORIZONTAL,
                              command=self.canvas.set_scale)
        self.scale.pack(side='right')

        self.scale_frame.pack(side='top', fill=tk.BOTH)
        self.scale.set(60)

    def _setup_capabilities(self):
        capabilities_frame = ttk.LabelFrame(self, text='Capabilities',
                                            padding=(6,6,6,6))
        capabilities_frame.pack(side='top', fill=tk.BOTH)
        self.capabilities_vars = {}
        for name, label in self.CAPABILITIES:
            var = tk.IntVar()
            self.capabilities_vars[name] = var
            ttk.Checkbutton(
                capabilities_frame,
                text=label,
                variable=var,
                command=(lambda name=name: self._update_capability(name))
            ).pack(side='top', anchor='w')

    def _setup_tools(self):
        tools_frame = ttk.LabelFrame(self, text='Tools',
                                     padding=(6,6,6,6))
        tools_frame.pack(side='top', fill=tk.BOTH)
        self._tool_id = tk.IntVar()

        # ttk.Label(self, text='Tool:').pack(side='top')
        for i, tool in enumerate(tools.TOOLS):
            ttk.Radiobutton(
                tools_frame,
                text=tool.name,
                variable=self._tool_id,
                value=i,
                command=(lambda i=i: self._set_tool(i)) # Force capture of i to avoid scoping issues
            ).pack(side='top', anchor='w')

        self._tool_id.set(0)
        self._set_tool(0)

    def _update_capability(self, name):
        if self.capabilities_vars[name].get():
            self.level.capabilities.append(name)
        else:
            self.level.capabilities.remove(name)

    def _set_tool(self, i):
        self.tool = tools.TOOLS[i](self.canvas, self.level)

    def _run(self):
        level = Level.deserialize(self.level.serialize())
        problem = level.planning_problem()
        plan = problem.solve()

        if plan is not None:
            LevelView(level, ActionSequence(level, plan)).start()
        else:
            messagebox.showerror("Planning failed", "No solution found")

    def _save(self):
        path = filedialog.asksaveasfilename(
            initialdir = 'levels/',
            title = 'Select file',
            defaultextension='.json')
        with open(path, 'w') as f:
            self.level.save(f)



class EditView:
    def __init__(self, level, width=800, height=600):
        self.level = level
        self.root = tk.Tk()
        self.app = tk.Frame(self.root)
        self.canvas = EditorCanvas(self.app, self.level, width=width, height=height)
        self.canvas.pack(side='left', fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self._mousedown)
        self.canvas.bind('<B1-Motion>', self._mousemove)
        self.canvas.bind('<ButtonRelease-1>', self._mouseup)

        self.edit_pane = ControlPanel(self.app, self.canvas, width=300)
        self.edit_pane.pack(side='right', fill=tk.BOTH)

        self.app.pack(fill=tk.BOTH, expand=True)

    def start(self):
        self.canvas.redraw()
        while True:
            try:
                self.root.mainloop()
                break
            except UnicodeDecodeError:
                pass

    def _mousedown(self, event):
        self.edit_pane.tool.mousedown(*self.canvas.preimage_point((event.x, event.y)))

    def _mousemove(self, event):
        self.edit_pane.tool.mousemove(*self.canvas.preimage_point((event.x, event.y)))

    def _mouseup(self, event):
        self.edit_pane.tool.mouseup(*self.canvas.preimage_point((event.x, event.y)))

    def _scroll(self, event):
        import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    level = Level()
    EditView(level).start()
