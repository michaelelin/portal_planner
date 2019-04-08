import json
import sys

from level import Level
from planning.predicates import *
from planning.objects import *

if __name__ == '__main__':
    filename = sys.argv[1]
    level = Level.load(filename)
    problem = level.planning_problem()
    print(problem.solve())
