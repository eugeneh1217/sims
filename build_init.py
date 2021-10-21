import argparse
import os

"""Command-line utility to automatically add __init__.py recusively:
    example: start at current directory (inclusive): "python -m build_init ."
"""

def write_init(path, added=None):
    init_path = os.path.join(path, '__init__.py')
    if not os.path.isfile(init_path):
        with open(init_path, 'w', encoding='utf-8') as init_file:
            init_file.close()
        if added == None:
            added = [init_path]
        else:
            added.append(init_path)
    for next_dir in os.listdir(path):
        next_dir_path = os.path.join(path, next_dir)
        if os.path.isdir(next_dir_path) and '.' not in next_dir:
            write_init(next_dir_path, added=added)
    return added

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('startdir', type=str)
    args = parser.parse_args()
    print(f"added: {write_init(args.startdir)}")
