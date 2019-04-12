import utils

from logic import Expression
from value import Binding

class Action:
    def __init__(self, name, parameters, precondition, effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

    def instantiate(self, args):
        return ActionInstance(self, args)

    @staticmethod
    def deserialize(expr, domain):
        action_name = utils.get_arg(expr, ':action')
        parameters = [Binding(param_name, domain.types[param_type])
                      for param_name, param_type in utils.typed_ids(utils.get_arg(expr, ':parameters'))]

        # Build an environment containing both our global constants and local parameters
        new_env = {**domain.constants, **{p.name: p for p in parameters}}
        precondition = Expression.deserialize(utils.get_arg(expr, ':precondition'),
                                              domain, new_env)
        effect = Expression.deserialize(utils.get_arg(expr, ':effect'),
                                        domain, new_env)
        return Action(action_name, parameters, precondition, effect)


class ActionInstance:
    def __init__(self, action, args):
        self.action = action
        self.args = args

    def apply(self, fluents):
        self.action.effect.apply(fluents, dict(zip(self.action.parameters, self.args)))

    def __repr__(self):
        return '(%s %s)' % (self.action.name, ' '.join([a.name for a in self.args]))
