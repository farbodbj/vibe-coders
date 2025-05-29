import argparse
import os
import sys

import dotenv

from utils.file_parser import FileParser

dotenv.load_dotenv()


def generate_file_tree(path):
    ret = []

    try:
        items = os.listdir(path)
    except OSError as e:
        print(f"Error reading directory {path}: {e}")
        return ret

    for i, item in enumerate(items):
        if item == 'venv':
            continue
        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            ret += generate_file_tree(item_path)
        elif item_path.endswith('.py'):
            ret.append(item_path)

    return ret


def run():
    agp = argparse.ArgumentParser()

    agp.add_argument(
        '--dir',
        default=os.getcwd(),
        help="Project repository directory",
    )

    args = agp.parse_args()

    project_dir = args.dir

    py_files = generate_file_tree(project_dir)

    print(py_files)

    for f in py_files:
        parser = FileParser(f)

        parser.analyze_file()


if __name__ == '__main__':
    run()
