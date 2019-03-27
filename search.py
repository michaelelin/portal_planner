import heapq

class SearchNode:
    def __init__(self, state, target, parent=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.path_cost = path_cost
        self.heuristic = state.distance(target)

    # Returns the list of states used to get to this node
    def history(self):
        if self.parent and isinstance(self.parent, SearchNode):
            return self.parent.history() + [self.state]
        elif self.parent:
            return [self.parent]
        else:
            return []

    def __lt__(self, other):
        return (self.path_cost + self.heuristic) < (other.path_cost + other.heuristic)

    def __repr__(self):
        return 'SearchNode[%s]' % self.state

class AStarSearch:
    def __init__(self, start, target):
        self.frontier = []
        self.frontier_costs = {}
        self.explored = set()
        self.start = start
        self.target = target

    def search(self):
        heapq.heappush(self.frontier, SearchNode(self.start, self.target, self.start))
        self.frontier_costs[self.start] = 0

        for node in self.explore_nodes():
            if node.state == self.target:
                return node.history()
            self.expand_node(node)
        raise Exception('Path to target not found')

    def explore_nodes(self):
        while self.frontier:
            node = heapq.heappop(self.frontier)
            if node.state not in self.explored:
                del self.frontier_costs[node.state]
                self.explored.add(node.state)
                yield node

    def expand_node(self, node):
        for neighbor in node.state.neighbors:
            path_cost = node.path_cost + node.state.distance(neighbor)
            if self.can_explore(neighbor, path_cost):
                # This might be a duplicate, but we can't easily change the
                # existing node entry. Instead, add another to the priority queue (with lower
                # priority) and ignore the old one if we run into it later.
                self.push_node(neighbor, node, path_cost)

    def push_node(self, state, parent, path_cost):
        heapq.heappush(self.frontier, SearchNode(state, self.target, parent, path_cost))
        self.frontier_costs[state] = path_cost

    def can_explore(self, state, path_cost):
        return (state not in self.explored and
                (state not in self.frontier_costs or path_cost < self.frontier_costs[state]))
