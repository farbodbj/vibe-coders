import argparse
import os
import sys

import dotenv

from models import CommonName, ProjectKnowledgeBase
from utils.file_parser import FileParser

dotenv.load_dotenv()

CONFIG_FILE_NAME = '.thevibebase.json'


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
    agp = argparse.ArgumentParser(
        prog="The Vibe Base: Ultimate code knowledgebase")

    agp.add_argument(
        '--dir',
        default=os.getcwd(),
        help="Project repository directory",
    )

    # agp.add_argument(
    #     '-C',
    #     '--use-config',
    #     action='store_true',
    #     help="Project repository directory",
    # )

    agp.add_argument(
        '--name',
        help="Project repository directory",
    )

    agp.add_argument(
        '--description',
        default='',
        help="Project repository directory",
    )

    agp.add_argument(
        '--common-names',
        dest="cnames",
        nargs=2,
        metavar=('type', 'name'),
        default=[],
        action='append',
        help="Project repository directory",
    )

    args = agp.parse_args()

    project_dir = args.dir

    project = None
    if os.path.exists(os.path.join(project_dir, CONFIG_FILE_NAME)):
        with open(os.path.join(project_dir, CONFIG_FILE_NAME), 'r') as f:
            project = ProjectKnowledgeBase.model_validate_json(f.read())
    else:
        project_name = args.name or os.path.dirname(project_dir)

        project = ProjectKnowledgeBase(
            name=project_name,
            description=args.description,

            common_names=[CommonName(type=t, name=n) for t, n in args.cnames],
        )

    py_files = generate_file_tree(project_dir)

    for f in py_files:
        parser = FileParser(project, f)

        # parser.analyze_file()

    json_output = project.model_dump_json()
    with open(os.path.join(project_dir, CONFIG_FILE_NAME), 'w') as conf:
        conf.write(json_output)


if __name__ == '__main__':
    run()
