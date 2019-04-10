import requests
import sexpdata

from .actions import actions, Pathfind

class Planner:
    def __init__(self, problem):
        self.problem = problem
        with open('planning/pddl/domain.pddl', 'r') as domain_file:
            self.domain = domain_file.read()

    def plan(self):
        problem_str = sexpdata.dumps(self.problem.serialize(), str_as='symbol')
        data = { 'domain': self.domain, 'problem': problem_str }
        r = requests.post('http://solver.planning.domains/solve', data=data)
        return self.parse_actions(r.json()['result']['plan'])

    def parse_actions(self, action_data):
        parsed = []
        for action in action_data:
            data = sexpdata.loads(action['name'])
            action_name = data[0].value()
            args = [self.problem.objects[arg.value()] for arg in data[1:]]
            parsed.append(actions[action_name](*args))
        # Append a final path to the goal
        parsed.append(Pathfind(self.problem.level.player, self.problem.level.goal))
        return parsed


