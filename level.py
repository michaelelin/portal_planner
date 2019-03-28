import json
import math

from entity import Entity
from search import AStarSearch
from wall import Wall

class Level:
    def __init__(self, walls, entities, start):
        self.walls = walls
        self.entities = entities
        self.start = start
        self._navigation = None

    def navigation(self):
        if not self._navigation:
            self._navigation = NavigationGraph(self.walls, self.start)
        return self._navigation

    def bounds(self):
        (x_min, y_min) = self.start
        (x_max, y_max) = self.start
        for wall in self.walls:
            x_min = min(x_min, wall.x1, wall.x2)
            y_min = min(y_min, wall.y1, wall.y2)
            x_max = max(x_max, wall.x1, wall.x2)
            y_max = max(y_max, wall.y1, wall.y2)
        return (x_min, y_min, x_max, y_max)

    def draw(self, canvas):
        for node in self.navigation().nodes.values():
            node.draw(canvas)
        for wall in self.walls:
            wall.draw(canvas)
        for entity in self.entities:
            entity.draw(canvas)

        start_x, start_y = self.start
        canvas.create_oval(start_x - 0.3, start_y - 0.3, start_x + 0.3, start_y + 0.3, fill='red')

    @staticmethod
    def load(filename):
        with open(filename) as f:
            obj = json.load(f)
        walls = sum((Wall.deserialize(wall) for wall in obj['walls']), []) # Concat the lists together
        entities = ([Entity.deserialize(entity) for entity in obj['entities']]
                    if 'entities' in obj else [])
        start = tuple(obj['start'])
        return Level(walls, entities, start)


class NavigationGraph:
    def __init__(self, walls, start):
        self.walls = walls
        self.build_graph(start)

    def build_graph(self, start):
        self.nodes = {}
        frontier = [start]
        explored = set([start])
        while frontier:
            pos = frontier.pop()
            if pos not in self.nodes:
                node = NavigationNode(pos)
                self.nodes[pos] = node
                (x, y) = pos
                for (dx, dy) in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    next_pos = (x + dx, y + dy)
                    if self.has_immediate_path(pos, next_pos):
                        if next_pos in self.nodes:
                            self.nodes[next_pos].add_neighbor(node)
                        elif next_pos not in explored:
                            frontier.append(next_pos)
                            explored.add(next_pos)

    def has_immediate_path(self, pos1, pos2):
        for wall in self.walls:
            if wall.intersects(pos1, pos2):
                return False
        return True

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
    def __init__(self, pos):
        self.x, self.y = pos
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        neighbor.neighbors.append(self)

    # Euclidean distance, this provides a more direct-looking route and will
    # generalize better in the future when we're not grid-based
    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def contains(self, x, y):
        return x >= self.x - 0.5 and x <= self.x + 0.5 and y >= self.y - 0.5 and y <= self.y + 0.5

    def draw(self, canvas):
        canvas.create_rectangle(self.x - 0.5, self.y - 0.5,
                                self.x + 0.5, self.y + 0.5,
                                outline="gray")

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return "(%s, %s), neighbors: %s" % (self.x, self.y, [(n.x, n.y) for n in self.neighbors])
