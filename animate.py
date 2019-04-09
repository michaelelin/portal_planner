class ActionSequence:
    def __init__(self, level, actions):
        self.level = level
        self.actions = actions

    def step(self):
        for action in self.actions:
            if not action.begun:
                action.begin(self.level)
            if not action.finished():
                action.step()
                return True
        return False
