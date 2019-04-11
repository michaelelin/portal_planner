import sexpdata

import utils
from value import Value
from logic import Expression, PredicateInstance

class Problem:
    def __init__(self, name, domain, objects, init, goal):
        self.name = name
        self.domain = domain
        self.objects = objects
        self.init = init
        self.goal = goal

    @staticmethod
    def load(filename, domain):
        with open(filename, 'r') as f:
            data = utils.desymbolize(sexpdata.load(f))
        return Problem.deserialize(data, domain)

    @staticmethod
    def deserialize(expr, domain):
        assert(expr[0] == 'define')
        assert(expr[1][0] == 'problem')
        problem_name = expr[1][1]

        domain = domain
        objects = {}
        init = []
        goal = None
        for form in expr[2:]:
            if form[0] == ':domain':
                assert(form[1] == domain.name)
            elif form[0] == ':objects':
                objects = Problem.deserialize_objects(form, domain)
            elif form[0] == ':init':
                init = Problem.deserialize_init(form, domain, objects)
            elif form[0] == ':goal':
                goal = Problem.deserialize_goal(form, domain, objects)

        return Problem(problem_name, domain, objects, init, goal)

    @staticmethod
    def deserialize_objects(expr, domain):
        assert(expr[0] == ':objects')
        objects = [Value(object_name, domain.types[object_type])
                   for object_name, object_type in utils.typed_ids(expr[1:])]
        return { o.name: o for o in objects }

    @staticmethod
    def deserialize_init(expr, domain, objects):
        assert(expr[0] == ':init')
        env = {**domain.constants, **objects}
        return [PredicateInstance.deserialize(form, domain, env) for form in expr[1:]]

    @staticmethod
    def deserialize_goal(expr, domain, objects):
        assert(expr[0] == ':goal')
        assert(len(expr) == 2)
        env = {**domain.constants, **objects}
        return Expression.deserialize(expr[1], domain, env)
