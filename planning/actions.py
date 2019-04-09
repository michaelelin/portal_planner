from .objects import *

class Action:
    begun = False

    def begin(self, level):
        self.level = level
        self._begin()
        self.begun = True

    def _begin(self):
        pass

    def step(self):
        raise Exception('step not implemented for %s' % self.__class__.__name__)

    def finished(self):
        raise Exception('finished not implemented for %s' % self.__class__.__name__)

# Sub-action that's useful for many others
class Pathfind(Action):
    EPSILON = 0.0001
    SPEED = 0.1

    def __init__(self, player, target):
        self.player = player
        self.target = target

    def _begin(self):
        self.path = self.level.navigation.search(self.player, self.target)
        self.index = 0

    def step(self):
        curr_node = self.path[self.index]
        next_node = self.path[self.index+1]
        self.player.move_toward(next_node, Pathfind.SPEED)
        if self.player.distance_squared(next_node) < Pathfind.EPSILON:
            self.index += 1

    def finished(self):
        return self.index >= len(self.path) - 1



class Move(Pathfind):
    def __init__(self, player, from_loc, to_loc):
        self.player = player
        self.from_loc = from_loc
        self.to_loc = to_loc

    def _begin(self):
        if isinstance(self.from_loc, Button):
            self.player.step_off(self.from_loc)

        if isinstance(self.to_loc, Button):
            self.path = self.level.navigation.search(self.player, self.to_loc)
        elif isinstance(self.to_loc, Room):
            room_center = self.to_loc.center()
            self.path = self.level.navigation.search_multiple(
                self.player,
                goal_test=(lambda pos: pos.room == self.to_loc),
                heuristic=(lambda pos: pos.distance(room_center))
            )
        self.index = 0

    def step(self):
        super().step()
        if isinstance(self.to_loc, Button) and self.finished():
            self.player.step_on(self.to_loc)



class PickUp(Action):
    def __init__(self, player, obj, loc):
        self.player = player
        self.obj = obj
        self.loc = loc

    def _begin(self):
        self.pathfinding = Pathfind(self.player, self.obj)
        self.pathfinding.begin(self.level)
        self._done = False

    def step(self):
        if self.pathfinding.finished():
            self.player.pick_up(self.obj)
            self._done = True
        else:
            self.pathfinding.step()

    def finished(self):
        return self._done

class PutDown(Action):
    def __init__(self, player, obj, loc):
        self.player = player
        self.obj = obj
        self.loc = loc

    def _begin(self):
        self.player.put_down(self.obj)

    def finished(self):
        return True

class EnterPortal(Action):
    def __init__(self, player, portal1, portal2, from_loc, to_loc):
        self.player = player
        self.portal1 = portal1
        self.portal2 = portal2
        self.from_loc = from_loc
        self.to_loc = to_loc

    def _begin(self):
        self.pathfinding = Pathfind(self.player, self.portal1)
        self.pathfinding.begin(self.level)
        self._done = False

    def step(self):
        if self.pathfinding.finished():
            self.player.move_to(self.portal2)
            self._done = True
        else:
            self.pathfinding.step()

    def finished(self):
        return self._done

class EnterDoor(Move):
    def __init__(self, player, door, from_loc, to_loc):
        self.player = player
        self.door = door
        self.from_loc = from_loc
        self.to_loc = to_loc

actions = {
    'move': Move,
    'pick-up': PickUp,
    'put-down': PutDown,
    'enter-portal': EnterPortal,
    'enter-door': EnterDoor,
}
