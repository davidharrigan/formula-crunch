import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def write_file(path, content):
    filename = os.path.join(ROOT_DIR, '..', 'data', path)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(content)


def get_file(path):
    filename = os.path.join(ROOT_DIR, '..', 'data', path)
    try:
        f = open(filename, 'r')
    except OSError:
        return None
    with f:
        content = f.read()
    return content
