import json
import os
from collections import defaultdict

import colors
from portal.entity import Entity, Player, Portal, Button
from portal.navigation import NavigationGraph
from portal.wall import Segment, WallSegment
from portal.planning.problem import Problem
from portal.geometry import Position, Segment

class Level:
    def __init__(self, name=None, walls=None, entities=None, start=None, goal=None,
                 capabilities=None):
        self.name = name
        self.walls = walls or []
        self.entities = entities or [Portal(None, None, 'portal1'), Portal(None, None, 'portal2')]
        self.entities_dict = { e.name: e for e in self.entities }
        self.start = start or Position(0, 0)
        self.goal = Goal(*goal.pos()) if goal else Goal(1, 0)
        self.capabilities = capabilities or []
        self.player = Player(self.start.x, self.start.y)
        self._navigation = None
        self._cache_walls()

    @property
    def navigation(self):
        if not self._navigation:
            self._navigation = NavigationGraph(self)
        return self._navigation

    def planning_problem(self):
        return Problem(self)

    def _cache_walls(self):
        x_min = self.start.x
        x_max = self.start.x
        y_min = self.start.y
        y_max = self.start.y
        for wall in self.walls:
            x_min = min(x_min, wall.x1, wall.x2)
            y_min = min(y_min, wall.y1, wall.y2)
            x_max = max(x_max, wall.x1, wall.x2)
            y_max = max(y_max, wall.y1, wall.y2)
        self.bounds = (x_min, y_min, x_max, y_max)

        self.wall_cache = defaultdict(set)
        for wall in self.walls:
            for cell in wall.intersecting_cells():
                self.wall_cache[cell].add(wall)

    def possible_intersections(self, pos1, pos2):
        intersections = set()
        for cell in Segment(pos1, pos2).intersecting_cells():
            intersections.update(self.wall_cache[cell])
        return intersections

    def segment_intersects(self, pos1, pos2, radius=0):
        s = Segment(pos1, pos2)
        rays = [s]
        if radius > 0 and pos1.pos() != pos2.pos():
            rays.append(s.offset(radius))
            rays.append(s.offset(-radius))

        for ray in rays:
            for segment in self.possible_intersections(ray.p1, ray.p2):
                if segment.intersects(ray.p1, ray.p2):
                    return segment

        return None


    def add_entity(self, entity):
        for i, e in enumerate(self.entities):
            if e.name == entity.name:
                del self.entities[i]
                break
        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)
        if isinstance(entity, Button):
            for wall in self.walls:
                if isinstance(wall, Door):
                    wall.triggers.remove(entity)

    def draw(self, canvas):
        canvas.create_text(10, 10, text=self.name,
                           anchor='nw',
                           font=('Arial', 20, 'bold'))
        # for node in self.navigation.nodes.values():
        #     node.draw(canvas)
        for wall in self.walls:
            wall.draw(canvas)
        self.goal.draw(canvas)
        for entity in self.entities:
            entity.draw(canvas)
        self.player.draw(canvas)

    def serialize(self):
        return {
            'name': self.name,
            'capabilities': self.capabilities,
            'walls': [w.serialize() for w in self.walls],
            'entities': [e.serialize() for e in self.entities],
            'start': [self.start.x, self.start.y],
            'goal': [self.goal.x, self.goal.y],
        }

    def save(self, f):
        json.dump(self.serialize(), f)

    @staticmethod
    def load(f):
        obj = json.load(f)
        return Level.deserialize(obj)

    @staticmethod
    def deserialize(obj):
        name = obj['name']
        entities = (sorted([Entity.deserialize(entity) for entity in obj['entities']],
                           key=lambda e: e.ORDER)
                    if 'entities' in obj else [])
        entities_dict = { e.name: e for e in entities }
        walls = sum((WallSegment.deserialize(wall, entities_dict) for wall in obj['walls']), []) # Concat the lists together
        start = Position(*obj['start'])
        goal = Position(*obj['goal'])
        capabilities = obj['capabilities']
        return Level(name, walls, entities, start, goal, capabilities)


class Goal(Position):
    def draw(self, canvas):
        canvas.create_oval(self.x - 0.1, self.y - 0.1,
                           self.x + 0.1, self.y + 0.1, fill=colors.GOAL)
