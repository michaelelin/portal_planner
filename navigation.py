import math

import planning.objects
from search import AStarSearch
from wall import *

PATH_NONE = 0
PATH_TO = 1
PATH_FROM = 2
PATH_BOTH = 3
PATH_DOOR = 4
PATH_GRILL = 5
class NavigationGraph:

    def __init__(self, level):
        self.level = level
        self.build_graph()

    def build_graph(self):
        self.nodes = {}
        self.rooms = []
        x_min, y_min, x_max, y_max = self.level.bounds()
        x_min = math.floor(x_min) - 1
        y_min = math.floor(y_min) - 1
        x_max = math.ceil(x_max)
        y_max = math.ceil(y_max)
        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                if (x, y) not in self.nodes:
                    room = Room()
                    self.fill_nodes((x, y), room, (x_min, y_min, x_max, y_max))
                    self.rooms.append(room)

    def fill_nodes(self, start, room, bounds):
        x_min, y_min, x_max, y_max = bounds
        frontier = [start]
        while frontier:
            pos = frontier.pop()
            if pos not in self.nodes:
                node = NavigationNode(pos, room)
                self.nodes[pos] = node
                (x, y) = pos
                for i, (dx, dy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
                    x_next = x + dx
                    y_next = y + dy
                    next_pos = (x_next, y_next)
                    if x_next < x_min or x_next > x_max or y_next < y_min or y_next > y_max:
                        continue

                    path_type, wall = self.immediate_path_type(pos, next_pos)
                    # If we've already explored this node, add the appropriate connections.
                    # If not, then if there's no wall between the two nodes, add it to our frontier.
                    # If there is a wall, leave it to be discovered (and potentially connected)
                    # later.
                    if next_pos in self.nodes:
                        next_node = self.nodes[next_pos]
                        if path_type in (PATH_BOTH, PATH_DOOR, PATH_GRILL):
                            node.add_neighbor(i, next_node, wall)
                            next_node.add_neighbor((i + 2) % 4, node, wall) # The opposite direction
                        elif path_type == PATH_TO:
                            node.add_neighbor(i, next_node, wall)
                        elif path_type == PATH_FROM:
                            next_node.add_neighbor((i + 2) % 4, node, wall)
                    elif path_type == PATH_BOTH:
                        frontier.append(next_pos)

    def immediate_path_type(self, pos1, pos2):
        for wall in self.level.walls:
            x1, y1 = pos1
            x2, y2 = pos2
            intersection = wall.intersects((x1 + 0.5, y1 + 0.5), (x2 + 0.5, y2 + 0.5))
            if intersection:
                if isinstance(wall, Door):
                    return PATH_DOOR, wall
                elif isinstance(wall, Grill):
                    return PATH_GRILL, wall
                elif isinstance(wall, Ledge):
                    return (PATH_TO if intersection > 0 else PATH_FROM), wall
                else:
                    return PATH_NONE, wall
        return PATH_BOTH, None

    def closest_node(self, pos):
        # Just search through the nodes linearly since nodes won't necessarily be laid out in a
        # grid. Could use a smarter algorithm in the future to prune the search space.
        for node in self.nodes.values():
            if node.contains(*pos):
                return node
        return None

    def search(self, start_pos, target_pos):
        start = self.closest_node(start_pos)
        target = self.closest_node(target_pos)
        if start and target:
            return AStarSearch(start, target).search()
        else:
            return None


class NavigationNode:
    def __init__(self, pos, room):
        self.x, self.y = pos
        self.room = room
        room.add_node(self)
        self.neighbors = [(None, None)] * 4 # East, North, West, South

    def add_neighbor(self, direction, neighbor, wall):
        self.neighbors[direction] = (neighbor, wall)

    # Euclidean distance, this provides a more direct-looking route and will
    # generalize better in the future when we're not grid-based
    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def contains(self, x, y):
        return x >= self.x and x <= self.x + 1 and y >= self.y and y <= self.y + 1

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y,
                                self.x + 1, self.y + 1,
                                outline="gray")

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return "(%s, %s), neighbors: %s" % (self.x, self.y, [(n.x, n.y) for n, _ in self.neighbors
                                                             if n is not None])


class Room(planning.objects.Room):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)
