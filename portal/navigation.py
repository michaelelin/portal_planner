import math

from portal.planning import objects
from portal.search import AStarSearch
from portal.wall import *
from portal.geometry import Position

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
        x_min, y_min, x_max, y_max = self.level.bounds
        x_min = math.floor(x_min) - 1
        y_min = math.floor(y_min) - 1
        x_max = math.ceil(x_max)
        y_max = math.ceil(y_max)

        self.fill_nodes((x_min, y_min), Room(), (x_min, y_min, x_max, y_max))
        outside = self.nodes
        self.nodes = {}

        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                if (x, y) not in self.nodes and (x, y) not in outside:
                    room = Room()
                    self.fill_nodes((x, y), room, (x_min, y_min, x_max, y_max))
                    self.rooms.append(room)
        for room in self.rooms:
            room.determine_walls()
        self.add_visibility()

    def fill_nodes(self, start, room, bounds):
        x_min, y_min, x_max, y_max = bounds
        frontier = [start]
        while frontier:
            pos = frontier.pop()
            if pos not in self.nodes:
                x, y = pos
                node = NavigationNode(x + 0.5, y + 0.5, room)
                self.nodes[pos] = node
                for i, (dx, dy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
                    x_next = x + dx
                    y_next = y + dy
                    next_pos = (x_next, y_next)
                    if x_next < x_min or x_next > x_max or y_next < y_min or y_next > y_max:
                        continue

                    if not self.add_neighbor(node, i, pos, next_pos):
                        frontier.append(next_pos)

    # Returns true if we've done everything we can right now, false if the next pos needs to be
    # added to the frontier
    def add_neighbor(self, node, direction, pos, next_pos):
        next_node = self.nodes.get(next_pos)
        x1, y1 = pos
        x2, y2 = next_pos
        p1 = Position(x1 + 0.5, y1 + 0.5)
        p2 = Position(x2 + 0.5, y2 + 0.5)
        for wall in self.level.possible_intersections(p1, p2):
            intersection = wall.intersects(p1, p2)
            # If we've already explored this node, add the appropriate connections.
            # If not, then if there's no wall between the two nodes, add it to our frontier.
            # If there is a wall, leave it to be discovered (and potentially connected)
            # later.
            if intersection:
                # Need special handling so we can determine which segments to create portals on
                if isinstance(wall, Wall):
                    for segment in wall.segments:
                        if segment.intersects(p1, p2):
                            node.add_neighbor(direction, None, segment, intersection)
                elif next_node:
                    if isinstance(wall, Door) or isinstance(wall, Grill):
                        path_from = True
                        path_to = True
                    elif isinstance(wall, Ledge) and intersection > 0:
                        path_from = True
                        path_to = False
                    elif isinstance(wall, Ledge) and intersection < 0:
                        path_from = False
                        path_to = True

                    node.add_neighbor(direction, (next_node if path_from else None), wall, intersection)
                    next_node.add_neighbor((direction + 2) % 4, (node if path_to else None), wall, -intersection)
                return True

        # No wall intersection
        if next_node:
            node.add_neighbor(direction, next_node, None, 0)
            next_node.add_neighbor((direction + 2) % 4, node, None, 0)
            return True
        else:
            return False

    # This is a stupid number of nested loops, I'm sure we could do something more clever
    def add_visibility(self):
        for node in self.nodes.values():
            for room in self.rooms:
                visible_segments = []
                for segment, direction in room.wall_segments:
                    # Check if we're coming at the wall from the right direction
                    if segment.intersects(node, segment.center()) == direction:
                        if self.is_segment_visible(segment, node):
                            visible_segments.append(segment)
                node.visible_rooms[room] = visible_segments

    def is_segment_visible(self, segment, node):
        for other_wall in self.level.possible_intersections(node, segment.center()):
            if ((not isinstance(other_wall, Ledge)) and other_wall != segment.parent and
                    other_wall.intersects(node, segment.center())):
                return False
        return True

    def closest_node(self, pos):
        # Just search through the nodes linearly since nodes won't necessarily be laid out in a
        # grid. Could use a smarter algorithm in the future to prune the search space.
        for node in self.nodes.values():
            if node.contains(pos):
                return node
        return None

    def closest_nodes(self, pos):
        for node in self.nodes.values():
            if node.contains(pos):
                yield node

    def search(self, start_pos, target_pos):
        start = self.closest_node(start_pos)
        targets = set(self.closest_nodes(target_pos))
        if start and targets:
            path = AStarSearch(start,
                               goal_test=(lambda pos: pos in targets),
                               heuristic=(lambda pos: pos.distance(target_pos))).search()
            if path is None:
                return None

            if path[0].x != start_pos.x or path[0].y != start_pos.y:
                path.insert(0, start_pos)
            if path[-1].x != target_pos.x or path[-1].x != target_pos.y:
                path.append(target_pos)
            return path
        else:
            return None

    def search_multiple(self, start_pos, goal_test, heuristic):
        start = self.closest_node(start_pos)
        if start:
            path = AStarSearch(start, goal_test, heuristic).search()
            if path is None:
                return None

            if path[0].x != start_pos.x or path[0].y != start_pos.y:
                path.insert(0, start_pos)
            return path
        else:
            return None


class NavigationNode(Position):
    def __init__(self, x, y, room):
        super().__init__(x, y)
        self.room = room
        room.add_node(self)
        self.neighbors = [(None, None, 0)] * 4 # East, North, West, South; (neighbor, wall, side)
        self.visible_rooms = {} # Map from room to list of wall segments

    def add_neighbor(self, direction, neighbor, wall, side):
        self.neighbors[direction] = (neighbor, wall, side)

    def contains(self, pos):
        return (pos.x >= self.x - 0.5 and pos.x <= self.x + 0.5 and
                pos.y >= self.y - 0.5 and pos.y <= self.y + 0.5)

    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.5, self.y - 0.5,
                                self.x + 0.5, self.y + 0.5,
                                outline="gray")

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return "(%s, %s), neighbors: %s" % (self.x, self.y, [(n.x, n.y) for n, _, _ in self.neighbors
                                                             if n is not None])


class Room(objects.Room):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def determine_walls(self):
        self.wall_segments = set()
        for node in self.nodes:
            for _, segment, direction in node.neighbors:
                if segment and segment.parent and isinstance(segment.parent, Wall):
                    self.wall_segments.add((segment, direction))

    def center(self):
        min_x = self.nodes[0].x
        max_x = self.nodes[0].x
        min_y = self.nodes[0].y
        max_y = self.nodes[0].y
        for node in self.nodes:
            min_x = min(min_x, node.x)
            max_x = max(max_x, node.x)
            min_y = min(min_y, node.y)
            max_y = max(max_y, node.y)
        return Position((min_x + max_x) * 0.5, (min_y + max_y) * 0.5)
