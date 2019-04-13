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

class Segment:
    def __init__(self, pos1, pos2):
        self.p1 = Position(*(pos1.pos() if isinstance(pos1, Position) else pos1))
        self.p2 = Position(*(pos2.pos() if isinstance(pos2, Position) else pos2))
        self.x1, self.y1 = self.p1.pos()
        self.x2, self.y2 = self.p2.pos()
        self.x_min = min(self.x1, self.x2)
        self.x_max = max(self.x1, self.x2)
        self.y_min = min(self.y1, self.y2)
        self.y_max = max(self.y1, self.y2)

    def offset(self, offset):
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        dist = math.sqrt(dx * dx + dy * dy)
        offset_x = dy * offset / dist
        offset_y = -dx * offset / dist
        return Segment((self.x1 + offset_x, self.y1 + offset_y),
                       (self.x2 + offset_x, self.y2 + offset_y))

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

    # Yields (x, y) integer pairs of cells this segment may have came into contact with
    # TODO Raytrace to make this smarter
    def intersecting_cells(self):
        for x in range(math.floor(self.x_min), math.ceil(self.x_max) + 1):
            for y in range(math.floor(self.y_min), math.ceil(self.y_max) + 1):
                yield (x, y)

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

