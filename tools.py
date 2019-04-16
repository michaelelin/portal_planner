import colors
from portal.geometry import Position
from portal.wall import Wall, PortalWall, Ledge, Door, Grill
from portal.entity import Portal, Cube, Button

class Tool:
    def __init__(self, canvas, level):
        self.canvas = canvas
        self.level = level
        self.setup()

    def setup(self):
        pass

    def mousedown(self, x, y):
        pass

    def mousemove(self, x, y):
        pass

    def mouseup(self, x, y):
        pass

class PlayerTool(Tool):
    name = 'Place player'
    def mousedown(self, x, y):
        p = Position(round(x * 2) * 0.5, round(y * 2) * 0.5)
        self.level.start.move_to(p)
        self.level.player.move_to(p)
        self.canvas.redraw()

class GoalTool(Tool):
    name = 'Place goal'
    def mousedown(self, x, y):
        p = Position(round(x * 2) * 0.5, round(y * 2) * 0.5)
        self.level.goal.move_to(p)
        self.canvas.redraw()


class SegmentTool(Tool):
    def setup(self):
        self.pos1 = None

    def mousedown(self, x, y):
        self.pos1 = Position(round(x), round(y))

    def mousemove(self, x, y):
        if self.pos1:
            pos2 = self._closest_position(round(x), round(y))
            self.canvas.redraw()
            if self.pos1.pos() != pos2.pos():
                segment = self._make_segment(self.pos1, pos2)
                segment.draw(self.canvas)

    def mouseup(self, x, y):
        if self.pos1:
            pos2 = self._closest_position(round(x), round(y))
            if self.pos1.pos() != pos2.pos():
                segment = self._make_segment(self.pos1, pos2)
                self.level.walls.append(segment)
            self.canvas.redraw()
        self.pos1 = None

    def _closest_position(self, x, y):
        if abs(x - self.pos1.x) > abs(y - self.pos1.y):
            return Position(x, self.pos1.y)
        else:
            return Position(self.pos1.x, y)

    def _make_segment(self, pos1, pos2):
        raise NotImplementedError

class WallTool(SegmentTool):
    name = 'Wall'
    def _make_segment(self, pos1, pos2):
        return Wall(pos1, pos2)

class PortalWallTool(SegmentTool):
    name = 'Portalable wall'
    def _make_segment(self, pos1, pos2):
        return PortalWall(pos1, pos2)

class LedgeTool(SegmentTool):
    name = 'Ledge'
    def _make_segment(self, pos1, pos2):
        return Ledge(pos1, pos2)

class DoorTool(SegmentTool):
    name = 'Door'
    def _make_segment(self, pos1, pos2):
        return Door(pos1, pos2, [])

class GrillTool(SegmentTool):
    name = 'Grill'
    def _make_segment(self, pos1, pos2):
        return Grill(pos1, pos2)

class PortalTool(Tool):
    def setup(self):
        self.pos1 = None

    def mousedown(self, x, y):
        self.pos1 = Position(round(x * 2) * 0.5, round(y * 2) * 0.5)

    def mousemove(self, x, y):
        if self.pos1:
            pos2 = self._closest_position(x, y)
            self.canvas.redraw()
            if self.pos1.pos() != pos2.pos():
                portal = self._make_portal(self.pos1, pos2)
                portal.draw(self.canvas)

    def mouseup(self, x, y):
        if self.pos1:
            pos2 = self._closest_position(x, y)
            if self.pos1.pos() != pos2.pos():
                portal = self._make_portal(self.pos1, pos2)
                self.level.add_entity(portal)
            self.canvas.redraw()
        self.pos1 = None

    def _closest_position(self, x, y):
        x = round(x * 2) * 0.5
        y = round(y * 2) * 0.5
        if x == self.pos1.x and y == self.pos1.y:
            return Position(x, y)
        if abs(x - self.pos1.x) > abs(y - self.pos1.y):
            if x > self.pos1.x:
                return Position(self.pos1.x + 1, self.pos1.y)
            else:
                return Position(self.pos1.x - 1, self.pos1.y)
        else:
            if y > self.pos1.y:
                return Position(self.pos1.x, self.pos1.y + 1)
            else:
                return Position(self.pos1.x, self.pos1.y - 1)

    def _make_portal(self, pos1, pos2):
        raise NotImplementedError

class Portal1Tool(PortalTool):
    name = 'Orange portal'
    def _make_portal(self, pos1, pos2):
        return Portal(pos1, pos2, 'portal1')

class Portal2Tool(PortalTool):
    name = 'Blue portal'
    def _make_portal(self, pos1, pos2):
        return Portal(pos1, pos2, 'portal2')

class CubeTool(Tool):
    name = 'Cube'
    def mousedown(self, x, y):
        cube = Cube(round(x * 2) * 0.5, round(y * 2) * 0.5)
        self.level.add_entity(cube)
        self.canvas.redraw()

class ButtonTool(Tool):
    name = 'Button'
    def mousedown(self, x, y):
        button = Button(round(x * 2) * 0.5, round(y * 2) * 0.5)
        self.level.add_entity(button)
        self.canvas.redraw()

class TriggerTool(Tool):
    name = 'Connect door to button'
    def setup(self):
        self.door = None
        self.button = None

    def mousedown(self, x, y):
        door = self._get_door(x, y)
        button = self._get_button(x, y)
        if door and button:
            if door.center().distance(Position(x, y)) < button.distance(Position(x, y)):
                self.door = door
            else:
                self.button = button
        elif door:
            self.door = door
        elif button:
            self.button = button

    def mousemove(self, x, y):
        if self.door:
            self.canvas.redraw()
            button = self._get_button(x, y)
            if button:
                self._draw_trigger(self.door.center(), button)
            else:
                self._draw_trigger(self.door.center(), Position(x, y))
        elif self.button:
            self.canvas.redraw()
            door = self._get_door(x, y)
            if door:
                self._draw_trigger(self.button, door.center())
            else:
                self._draw_trigger(self.button, Position(x, y))

    def mouseup(self, x, y):
        if self.door:
            button = self._get_button(x, y)
            if button and button not in self.door.triggers:
                self.door.triggers.append(button)
        elif self.button:
            door = self._get_door(x, y)
            if door and self.button not in door.triggers:
                door.triggers.append(self.button)
        self.door = None
        self.button = None
        self.canvas.redraw()

    def _draw_trigger(self, pos1, pos2):
        self.canvas.create_line(pos1.x, pos1.y, pos2.x, pos2.y,
                                width=2.0,
                                dash=(8, 8),
                                fill=colors.TRIGGER)

    def _get_door(self, x, y):
        for wall in self.level.walls:
            if isinstance(wall, Door) and wall.center().distance(Position(x, y)) < 0.5:
                return wall

    def _get_button(self, x, y):
        for entity in self.level.entities:
            if isinstance(entity, Button) and entity.distance(Position(x, y)) < 0.5:
                return entity

class EraserTool(Tool):
    name = 'Eraser'
    def setup(self):
        self.last_x = None
        self.last_y = None

    def mousedown(self, x, y):
        self._remove_entities(x, y)
        self.canvas.redraw()
        self.last_x = x
        self.last_y = y

    def mousemove(self, x, y):
        if self.last_x is not None and self.last_y is not None:
            self._remove_entities(x, y)
            self._remove_walls(self.last_x, self.last_y, x, y)
            self.canvas.redraw()
            self.last_x = x
            self.lats_y = y

    def mouseup(self, x, y):
        self.last_x = None
        self.last_y = None

    def _remove_entities(self, x, y):
        to_remove = []
        for e in self.level.entities:
            if e.x is not None and e.y is not None and e.distance(Position(x, y)) < 0.2:
                to_remove.append(e)
        for e in to_remove:
            self.level.remove_entity(e)

    def _remove_walls(self, x1, y1, x2, y2):
        to_remove = []
        for wall in self.level.walls:
            if wall.intersects(Position(x1, y1), Position(x2, y2)):
                to_remove.append(wall)
        for wall in to_remove:
            self.level.walls.remove(wall)



TOOLS = [
    PlayerTool,
    GoalTool,
    WallTool,
    PortalWallTool,
    LedgeTool,
    DoorTool,
    GrillTool,
    Portal1Tool,
    Portal2Tool,
    CubeTool,
    ButtonTool,
    TriggerTool,
    EraserTool,
]
