import math

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return (self.x, self.y)

    def distance_squared(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return dx * dx + dy * dy

    def distance(self, other):
        return math.sqrt(self.distance_squared(other))

    def move_toward(self, target, speed):
        distance = self.distance(target)
        if speed >= distance:
            self.x = target.x
            self.y = target.y
        else:
            self.x += (target.x - self.x) * speed / distance
            self.y += (target.y - self.y) * speed / distance
        self._updated_position()

    def move_to(self, target):
        self.x = target.x
        self.y = target.y
        self._updated_position()

    def _updated_position(self):
        pass

def offset_line(x1, y1, x2, y2, offset):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    offset_x = dy * offset / dist
    offset_y = -dx * offset / dist
    return (x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y)
