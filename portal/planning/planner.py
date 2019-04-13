import requests
import sexpdata

from planner.domain import Domain
from planner.problem import Problem
from portal.planning.actions import actions, Pathfind
from planner import utils

DOMAIN_PATH = 'pddl/domain.pddl'

class RemotePlanner:
    def __init__(self, problem):
        self.problem = problem
        with open(DOMAIN_PATH, 'r') as domain_file:
            self.domain = domain_file.read()

    def plan(self):
        problem_str = sexpdata.dumps(self.problem.serialize(), str_as='symbol')
        data = { 'domain': self.domain, 'problem': problem_str }
        r = requests.post('http://solver.planning.domains/solve', data=data).json()
        if 'plan' in r['result']:
            return self.parse_actions(r['result']['plan'])
        else:
            print(r['result']['error'])
            raise Exception('planning failed')

    def parse_actions(self, action_data):
        parsed = []
        for action in action_data:
            data = utils.desymbolize(sexpdata.loads(action['name']))
            action_name = data[0]
            args = [self.problem.objects[arg] for arg in data[1:]]
            parsed.append(actions[action_name](*args))
        # Append a final path to the goal
        parsed.append(Pathfind(self.problem.level.player, self.problem.level.goal))
        return parsed


class ForwardSearchPlanner:
    def __init__(self, portal_problem):
        self.portal_problem = portal_problem
        with open(DOMAIN_PATH, 'r') as f:
            self.domain = Domain.load(f)
        self.problem = Problem.deserialize(portal_problem.serialize(), self.domain)

    def plan(self):
        return self.parse_actions([a.serialize() for a in self.problem.plan()])

    def parse_actions(self, action_data):
        parsed = []
        for action in action_data:
            action_name = action[0]
            args = [self.portal_problem.objects[arg] for arg in action[1:]]
            parsed.append(actions[action_name](*args))
        # Append a final path to the goal
        parsed.append(Pathfind(self.portal_problem.level.player, self.portal_problem.level.goal))
        return parsed
