import sexpdata

def desymbolize(expr):
    if isinstance(expr, list):
        return [desymbolize(elt) for elt in expr]
    elif isinstance(expr, sexpdata.Symbol):
        return expr.value()
    else:
        return expr

def typed_ids(args):
    for i in range(0, len(args), 3):
        assert args[i+1] == '-'
        yield (args[i], args[i+2])

def get_arg(args, keyword, default=None):
    for i, arg in enumerate(args):
        if arg == keyword:
            return args[i + 1]
    return default
