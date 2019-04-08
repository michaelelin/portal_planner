import json
import os

from entity import Entity
from navigation import NavigationGraph
from wall import Wall
from planning.problem import Problem

class Level:
    def __init__(self, name, walls, entities, start, goal):
        self.name = name
        self.walls = walls
        self.entities = entities
        self.start = start
        self.goal = goal
        self._navigation = None

    @property
    def navigation(self):
        if not self._navigation:
            self._navigation = NavigationGraph(self)
        return self._navigation

    def planning_problem(self):
        return Problem(self)

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
        for node in self.navigation.nodes.values():
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
        name = obj['name']
        walls = sum((Wall.deserialize(wall) for wall in obj['walls']), []) # Concat the lists together
        entities = ([Entity.deserialize(entity) for entity in obj['entities']]
                    if 'entities' in obj else [])
        start = tuple(obj['start'])
        goal = tuple(obj['goal'])
        return Level(name, walls, entities, start, goal)
