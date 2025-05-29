import argparse
import os
import sys

import dotenv
import tree_sitter
import tree_sitter_python as tspython
from openai import OpenAI

import gitignore

dotenv.load_dotenv()


client = OpenAI(
    base_url="https://api.metisai.ir/openai/v1"
)

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
        elif item_path.endswith('.py'):
            ret.append(item_path)

    return ret


def get_method_name(node: tree_sitter.Node):
    for child in node.children:
        if child.type == 'identifier':
            return child.text.decode()
    return None


def generate_doc(ts: tree_sitter.Node, file_bytes):
    source = file_bytes[ts.start_byte:ts.end_byte].decode('utf-8')
    print(source)
    response = client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {"role": "system", "content": f"""
Your task is to generate a doc string along with definitions for this {ts.type}
            """},
            {"role": "user", "content": source},
        ]
    )
    print(get_method_name(ts), response.output_text)


def generate_methods(ts: tree_sitter.Node, file_bytes, indt: str = ""):
    for node in ts.children:
        print(indt, node.type)
        if node.type == 'function_definition':
            generate_doc(node, file_bytes)

        if node.type == 'class_definition':
            generate_doc(node, file_bytes)
            generate_methods(node, file_bytes, indt + '---')


lang = tree_sitter.Language(tspython.language())
parser = tree_sitter.Parser(lang)


def analyze_file(path):
    with open(path, 'r') as file:
        bts = file.read().encode()
        file_tree = parser.parse(bts)

        generate_methods(file_tree.root_node, bts, "")


def run():
    agp = argparse.ArgumentParser()

    agp.add_argument(
        '--dir',
        default=os.getcwd(),
        help="Project repository directory",
    )

    args = agp.parse_args()

    project_dir = args.dir

    gitignore_patterns = gitignore.load_patterns(project_dir)

    py_files = generate_file_tree(project_dir, gitignore_patterns)

    print(py_files)

    # for f in py_files:
    #     analyze_file(f)


if __name__ == '__main__':
    run()
