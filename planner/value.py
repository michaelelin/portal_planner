import utils


class Value:
    def __init__(self, name, typ):
        self.name = name
        self.type = typ

    def belongs_to(self, typ):
        return self.type.subtype(typ)

    def __repr__(self):
        return 'Value(name=%s, type=%s)' % (self.name, self.type.name)

class Binding(Value):
    def __repr__(self):
        return 'Binding(name=%s, type=%s)' % (self.name, self.type.name)


class Type:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

    def subtype(self, typ):
        return self == typ or (self.parent and self.parent.subtype(typ))

    def __repr__(self):
        return 'Type(name=%s, parent=%s)' % (self.name,
                                             (self.parent.name if self.parent else self.parent))
