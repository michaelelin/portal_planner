import sexpdata

import utils
from actions import Action
from value import Value, Type
from logic import Predicate

class Domain:
    def __init__(self, name, types=None, constants=None, predicates=None, actions=None):
        self.name = name
        self.types = types or {}
        self.constants = constants or []
        self.predicates = predicates or {}
        self.actions = actions or {}

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            data = utils.desymbolize(sexpdata.load(f))
        return Domain.deserialize(data)

    @staticmethod
    def deserialize(expr):
        assert(expr[0] == 'define')
        assert(expr[1][0] == 'domain')
        domain = Domain(expr[1][1])

        for form in expr[2:]:
            if form[0] == ':types':
                domain.types = Domain.deserialize_types(form, domain)
            elif form[0] == ':constants':
                domain.constants = Domain.deserialize_constants(form, domain)
            elif form[0] == ':predicates':
                domain.predicates = Domain.deserialize_predicates(form, domain)
            elif form[0] == ':action':
                action = Action.deserialize(form, domain)
                domain.actions[action.name] = action
        return domain

    @staticmethod
    def deserialize_types(expr, domain):
        assert(expr[0] == ':types')

        types = { 'object': Type('object') }

        for type_name, parent_type in utils.typed_ids(expr[1:]):
            types[type_name] = Type(type_name, types[parent_type])
        return types

    @staticmethod
    def deserialize_constants(expr, domain):
        assert(expr[0] == ':constants')

        constants = {}
        for constant_name, constant_type in utils.typed_ids(expr[1:]):
            constants[constant_name] = Value(constant_name, domain.types[constant_type])
        return constants

    @staticmethod
    def deserialize_predicates(expr, domain):
        assert(expr[0] == ':predicates')

        predicates = {}
        for predicate in expr[1:]:
            predicate_name = predicate[0]
            arg_types = [domain.types[arg_type] for arg_name, arg_type in utils.typed_ids(predicate[1:])]
            predicates[predicate_name] = Predicate(predicate_name, arg_types)
        return predicates
