import json
import sys

from animate import ActionSequence
from level import Level
from planning.predicates import *
from planning.objects import *
from view import LevelView

if __name__ == '__main__':
    filename = sys.argv[1]
    level = Level.load(filename)
    problem = level.planning_problem()
    plan = problem.solve()
    print(plan)

    view = LevelView(level, ActionSequence(level, plan))
    view.start()
