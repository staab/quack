import re, os, sys, itertools
from contextlib import contextmanager

# Helpers

_ctx = {
    'filename': 'anonymous',
    'line_number': None,
    'indent': 0,
    'parent': None,
}

@contextmanager
def ctx(**kw):
    global _ctx
    old_ctx = _ctx.copy()

    _ctx.update(kw)

    yield

    _ctx = old_ctx


class multimethod():
    def __init__(self, dispatch):
        self._dispatch = dispatch
        self._methods = {}
        self._default = None

    def __call__(self, *a, **kw):
        k = self._dispatch(*a, **kw)
        f = self._methods.get(k, self._default)

        if not f:
            raise KeyError(k)

        return f(*a, **kw)

    def method(self, k):
        def add_method(f):
            self._methods[k] = f

        return add_method

    def default(self, f):
        self._default = f

# Parsing functions


def parse_error(message):
    filename = _ctx.get('filename')
    line_number = _ctx.get('line_number')

    sys.stderr.write(f"Syntax Error: {message}\n")
    sys.stderr.write(f'  File "{filename}, line {line_number}"\n')
    sys.exit(1)


def parse_directory(dir):
    tree = get_node('root')
    for path, _, filenames in os.walk(dir):
        for filename in filenames:
            full_path = os.path.join(path, filename)
            with ctx(filename=full_path):
                with open(full_path, 'r') as f:
                    root = parse_text(f.read())
                    tree['children'].extend(root['children'])

    return tree


def parse_text(text):
    tree = get_node('root')
    node = tree

    for line_number, line in enumerate(text.split("\n"), start=1):
        with ctx(line_number=line_number):
            line = re.sub('\s*(#.*)$', '', line)

            if not line:
                continue

            indent = len(re.match(r'^\s*', line).group(0))

            if node['type'] == 'root' and indent:
                parse_error("Found an indented block outside a parent block")

            while indent < node['indent']:
                node = node['parent']

            with ctx(indent=indent, parent=node):
                new_node = get_node(line)

            node['children'].append(new_node)

            if node['type'] == 'root' or new_node['indent'] > node['indent']:
                node = new_node

    return tree


# node creation


def get_node(line, **kw):
    parts = re.split('\s+', line.strip())
    type = get_node_type(line, parts, **kw)
    attrs = get_node_attrs(line, parts)

    node = {
        'type': type,
        'attrs': attrs,
        'children': [],
    }

    node.update(_ctx)

    return node


def get_node_type(line, parts, rh=False):
    if len(parts) >= 3 and parts[1] == '=':
        return 'assignment'
    if re.match('^".*"$', line):
        return 'string'
    if len(parts) == 1 and re.match('^\d*\.?\d+', line):
        return 'number'
    elif parts[0].lower() in get_node_attrs._methods:
        return parts[0].lower()
    elif len(parts) == 1:
        return 'symbol'

    parse_error(f"Invalid keyword: {parts[0]}")


@multimethod
def get_node_attrs(line, parts):
    return get_node_type(line, parts)


@get_node_attrs.method('root')
def get_root_node_attrs(line, parts):
    return {}


@get_node_attrs.method('app')
def get_app_node_attrs(line, parts):
    return {}


@get_node_attrs.method('string')
def get_string_node_attrs(line, parts):
    return {}


@get_node_attrs.method('symbol')
def get_symbol_node_attrs(line, parts):
    return {'name': line}


@get_node_attrs.method('assignment')
def get_assignment_node_attrs(line, parts):
    return {
        'name': parts[0],
        'value': get_node(' '.join(parts[2:]), rh=True),
    }


@get_node_attrs.method('data')
def get_data_node_attrs(line, parts):
    return {'name': parts[1]}


@get_node_attrs.method('view')
def get_view_node_attrs(line, parts):
    return {'name': parts[1]}


@get_node_attrs.method('model')
def get_view_node_attrs(line, parts):
    return {'names': parts[1:]}


@get_node_attrs.method('component')
def get_view_node_attrs(line, parts):
    return {'name': parts[1]}


@get_node_attrs.method('show')
def get_view_node_attrs(line, parts):
    return {'name': parts[1]}


# Entrypoint


if __name__ == '__main__':
    print('\n--------')
    list(parse_directory('example'))
