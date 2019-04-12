import utils
from value import Binding


class Expression:
    def test(self, state, env={}):
        raise NotImplementedError('test not implemented for %s' % self.__class__.__name__)

    def apply(self, fluents, env={}):
        raise NotImplementedError('apply not implemented for %s' % self.__class__.__name__)

    @staticmethod
    def deserialize(expr, domain, env):
        op = expr[0]
        if op == 'and':
            expr_class = And
        elif op == 'or':
            expr_class = Or
        elif op == 'not':
            expr_class = Not
        elif op == 'imply':
            expr_class = Implies
        elif op == 'exists':
            expr_class = Exists
        elif op == 'forall':
            expr_class = Forall
        elif op == '=':
            expr_class = Equal
        else:
            expr_class = PredicateInstance
        return expr_class.deserialize(expr, domain, env)


class Predicate:
    def __init__(self, name, arg_types):
        self.name = name
        self.arg_types = arg_types

    def instantiate(self, args):
        assert(len(args) == len(self.arg_types))
        for arg, arg_type in zip(args, self.arg_types):
            assert(arg.belongs_to(arg_type))
        return PredicateInstance(self, args)

    def __repr__(self):
        return '(%s %s)' % (self.name, ' '.join([t.name for t in self.arg_types]))

class PredicateInstance(Expression):
    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = tuple(args)

    def test(self, state, env={}):
        if not state.fluents:
            import ipdb; ipdb.set_trace()
        return self.substitute(env) in state.fluents

    def apply(self, fluents, env={}):
        fluents.add(self.substitute(env))

    def substitute(self, env):
        return PredicateInstance(self.predicate, [arg.substitute(env) for arg in self.args])

    def __hash__(self):
        return hash((self.predicate, self.args))

    def __eq__(self, other):
        return self.predicate == other.predicate and self.args == other.args

    def __repr__(self):
        return '(%s %s)' % (self.predicate.name, ' '.join([a.name for a in self.args]))

    @staticmethod
    def deserialize(expr, domain, env):
        predicate = domain.predicates[expr[0]]
        args = [env[arg] for arg in expr[1:]]
        return predicate.instantiate(args)


class And(Expression):
    def __init__(self, *args):
        self.args = args

    def test(self, state, env={}):
        for arg in self.args:
            if not arg.test(state, env):
                return False
        return True

    def apply(self, fluents, env={}):
        for arg in self.args:
            arg.apply(fluents, env)

    def __repr__(self):
        return '(and %s)' % ' '.join([str(a) for a in self.args])

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == 'and')
        args = [Expression.deserialize(arg, domain, env) for arg in expr[1:]]
        return And(*args)

class Or(Expression):
    def __init__(self, *args):
        self.args = args

    def test(self, state, env={}):
        for arg in self.args:
            if arg.test(state, env):
                return True
        return False

    def __repr__(self):
        return '(or %s)' % ' '.join([str(a) for a in self.args])

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == 'or')
        args = [Expression.deserialize(arg, domain, env) for arg in expr[1:]]
        return Or(*args)

class Not(Expression):
    def __init__(self, arg):
        self.arg = arg

    def test(self, state, env={}):
        return not self.arg.test(state, env)

    def apply(self, fluents, env={}):
        assert(isinstance(self.arg, PredicateInstance))
        fluents.discard(self.arg.substitute(env))

    def __repr__(self):
        return '(not %s)' % str(self.arg)

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == 'not')
        assert(len(expr) == 2)
        arg = Expression.deserialize(expr[1], domain, env)
        return Not(arg)

class Implies(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, state, env={}):
        return (not self.left.test(state, env)) or self.right.test(state, env)

    def __repr__(self):
        return '(imply %s %s)' % (str(self.left), str(self.right))

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == 'imply')
        assert(len(expr) == 3)
        left = Expression.deserialize(expr[1], domain, env)
        right = Expression.deserialize(expr[2], domain, env)
        return Implies(left, right)

class Exists(Expression):
    def __init__(self, vars, expr):
        self.vars = vars
        self.expr = expr

    def test(self, state, env={}):
        for binding in state.possible_bindings([v.type for v in self.vars]):
            new_env = {**env, **dict(zip(self.vars, binding))}
            if self.expr.test(state, new_env):
                return True
        return False

    def __repr__(self):
        return '(exists (%s) %s)' % (' '.join(v.name for v in self.vars), str(self.expr))

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == 'exists')
        assert(len(expr) == 3)
        vars = [Binding(var_name, domain.types[var_type])
                for var_name, var_type in utils.typed_ids(expr[1])]
        new_env = {**env, **{b.name: b for b in vars}}
        expr = Expression.deserialize(expr[2], domain, new_env)
        return Exists(vars, expr)

class Forall(Expression):
    def __init__(self, vars, expr):
        self.vars = vars
        self.expr = expr

    def test(self, state, env={}):
        for binding in state.possible_bindings([v.type for v in self.vars]):
            new_env = {**env, **dict(zip(self.vars, binding))}
            if not self.expr.test(state, new_env):
                return False
        return True

    def __repr__(self):
        return '(forall (%s) %s)' % (' '.join(v.name for v in self.vars), str(self.expr))

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == 'forall')
        assert(len(expr) == 3)
        vars = [Binding(var_name, domain.types[var_type])
                for var_name, var_type in utils.typed_ids(expr[1])]
        new_env = {**env, **{b.name: b for b in vars}}
        expr = Expression.deserialize(expr[2], domain, new_env)
        return Forall(vars, expr)

class Equal(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, state, env={}):
        return self.left.substitute(env) == self.right.substitute(env)

    def __repr__(self):
        return '(= %s %s)' % (str(self.left), str(self.right))

    @staticmethod
    def deserialize(expr, domain, env):
        assert(expr[0] == '=')
        assert(len(expr) == 3)
        left = env[expr[1]]
        right = env[expr[2]]
        return Equal(left, right)
