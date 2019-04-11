import json
import sys

from portal.animate import ActionSequence
from portal.level import Level
from view import LevelView

if __name__ == '__main__':
    filename = sys.argv[1]
    level = Level.load(filename)
    problem = level.planning_problem()
    plan = problem.solve()

    view = LevelView(level, ActionSequence(level, plan),
                     width=800, height=580)
    view.start()
