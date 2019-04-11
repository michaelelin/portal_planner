import json
import os

from portal.entity import Entity, Player
from portal.navigation import NavigationGraph
from portal.wall import Segment
from portal.planning.problem import Problem
from portal.geometry import Position

class Level:
    def __init__(self, name, walls, entities, start, goal, capabilities):
        self.name = name
        self.walls = walls
        self.entities = entities
        self.entities_dict = { e.name: e for e in entities }
        self.start = start
        self.player = Player(start.x, start.y)
        self.goal = goal
        self.capabilities = capabilities
        self._navigation = None

    @property
    def navigation(self):
        if not self._navigation:
            self._navigation = NavigationGraph(self)
        return self._navigation

    def planning_problem(self):
        return Problem(self)

    def bounds(self):
        x_min = self.start.x
        x_max = self.start.x
        y_min = self.start.y
        y_max = self.start.y
        for wall in self.walls:
            x_min = min(x_min, wall.x1, wall.x2)
            y_min = min(y_min, wall.y1, wall.y2)
            x_max = max(x_max, wall.x1, wall.x2)
            y_max = max(y_max, wall.y1, wall.y2)
        return (x_min, y_min, x_max, y_max)

    def draw(self, canvas):
        canvas.create_text(10, 10, text=self.name,
                           anchor='nw',
                           font=('Arial', 20, 'bold'))
        for node in self.navigation.nodes.values():
            node.draw(canvas)
        for wall in self.walls:
            wall.draw(canvas)
        for entity in self.entities:
            entity.draw(canvas)
        self.player.draw(canvas)

    @staticmethod
    def load(filename):
        with open(filename) as f:
            obj = json.load(f)
        name = obj['name']
        entities = (sorted([Entity.deserialize(entity) for entity in obj['entities']],
                           key=lambda e: e.ORDER)
                    if 'entities' in obj else [])
        entities_dict = { e.name: e for e in entities }
        walls = sum((Segment.deserialize(wall, entities_dict) for wall in obj['walls']), []) # Concat the lists together
        start = Position(*obj['start'])
        goal = Position(*obj['goal'])
        capabilities = obj['capabilities']
        return Level(name, walls, entities, start, goal, capabilities)