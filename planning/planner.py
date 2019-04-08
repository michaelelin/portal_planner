import requests

class Planner:
    def __init__(self, problem):
        self.problem = problem
        with open('planning/pddl/domain.pddl', 'r') as domain_file:
            self.domain = domain_file.read()

    def plan(self):
        data = { 'domain': self.domain, 'problem': self.problem.serialize() }
        r = requests.post('http://solver.planning.domains/solve', data=data)
        return [action['name'] for action in r.json()['result']['plan']]
