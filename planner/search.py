from collections import deque

class ForwardSearch:
    def __init__(self, problem):
        self.problem = problem
        self.start = SearchState.from_problem(problem)
        self.goal = problem.goal

        self.frontier = deque()
        self.explored = set()

    def search(self):
        self.frontier.append(SearchNode(self.start))
        for node in self.explore_nodes():
            if node.state.satisfies(self.goal):
                return node.history()
            self.expand_node(node)
        return None

    def explore_nodes(self):
        while self.frontier:
            node = self.frontier.popleft()
            if node.state not in self.explored:
                self.explored.add(node.state)
                yield node

    def expand_node(self, node):
        for action in node.state.possible_actions():
            successor = node.state.successor(action)
            if successor not in self.explored:
                self.frontier.append(SearchNode(successor, node, action))


class SearchNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

    def history(self):
        if self.parent:
            h = self.parent.history()
            h.append(self.action)
            return h
        else:
            return []

    def __lt__(self, other):
        return (self.path_cost + self.remaining_cost) < (other.path_cost + other.remaining_cost)

    def __repr__(self):
        return 'SearchNode[%s]' % self.state

class SearchState:
    def __init__(self, problem, fluents):
        self.problem = problem
        self.domain = problem.domain
        self.fluents = frozenset(fluents)

    def possible_actions(self):
        for action in self.domain.actions.values():
            for binding in self.possible_bindings([p.type for p in action.parameters]):
                if action.precondition.test(self, dict(zip(action.parameters, binding))):
                    yield action.instantiate(list(binding))

    # Destructively mutates accumulated return value after yielding
    def possible_bindings(self, binding_types, acc=None):
        if acc is None:
            acc = []
        if not binding_types:
            yield acc
        else:
            for obj in self.problem.objects_of_type[binding_types[0]]:
                acc.append(obj)
                for b in self.possible_bindings(binding_types[1:], acc):
                    yield b
                acc.pop()

    def successor(self, action):
        fluents = set(self.fluents)
        action.apply(fluents)
        return SearchState(self.problem, fluents)

    def satisfies(self, expr):
        return expr.test(self)

    def __hash__(self):
        return hash((self.problem, self.domain, self.fluents))

    def __eq__(self, other):
        return (self.problem == other.problem and
                self.domain == other.domain and
                self.fluents == other.fluents)

    @staticmethod
    def from_problem(problem):
        return SearchState(problem, problem.init)
