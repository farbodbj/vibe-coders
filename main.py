import argparse
import os
import sys

import dotenv

import gitignore
from models import CommonName, ProjectKnowledgeBase
from utils.directory_parser import parse_dir
from utils.file_parser import FileParser
from utils.helper import is_supported_file
from utils.spinner import Spinner

dotenv.load_dotenv()

CONFIG_FILE_NAME = '.thevibebase.json'


def generate_file_tree(path, gitignore_patterns: list[str]):
    ret = []

    try:
        items = os.listdir(path)
    except OSError as e:
        print(f"Error reading directory {path}: {e}")
        return ret

    for i, item in enumerate(items):

        # Check if this item should be ignored
        if gitignore.is_ignored(item, gitignore_patterns):

            continue

        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            ret += generate_file_tree(item_path, gitignore_patterns)
        elif is_supported_file(item_path):
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
        '--no-readmes',
        dest='no_readmes',
        action='store_true',
        help="If set, not readme files will be created",
    )

    agp.add_argument(
        '--name',
        help="Project name, if not provided, directory name will be used",
    )

    agp.add_argument(
        '--description',
        default='',
        help="Project description",
    )

    agp.add_argument(
        '--common-names',
        dest="cnames",
        nargs=2,
        metavar=('type', 'name'),
        default=[],
        action='append',
        help="Common names that this project might be refered to with",
    )

    args = agp.parse_args()

    project_dir = os.path.abspath(args.dir)

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
    gitignore_patterns = gitignore.load_patterns(project_dir)

    py_files = generate_file_tree(project_dir, gitignore_patterns)

    # s = Spinner("Generating Docs")

    if not project_dir.endswith('/'):
        project_dir += '/'

    for f in py_files:
        parser = FileParser(project, f, project_dir=project_dir)

        parser.analyze_file()

    parse_dir(
        path=project_dir,
        project=project,
        gitignore_patterns=gitignore_patterns,
        project_dir=project_dir,
        generate_readme_files=not args.no_readmes,
    )

    json_output = project.model_dump_json()
    with open(os.path.join(project_dir, CONFIG_FILE_NAME), 'w') as conf:
        conf.write(json_output)
    # s.done()


if __name__ == '__main__':
    run()
