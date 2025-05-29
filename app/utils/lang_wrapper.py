import argparse
import os
import sys

import dotenv
import tree_sitter
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from openai import OpenAI

dotenv.load_dotenv()


class CodeAnalyzer:
    def __init__(self, language_module, language_name, file_extension):
        self.language_module = language_module
        self.language_name = language_name
        self.file_extension = file_extension
        self.client = OpenAI(base_url="https://api.metisai.ir/openai/v1")
        self.parser = self._initialize_parser()

    def _initialize_parser(self):
        parser = Parser()
        language = Language(self.language_module.language())
        parser.language = language  # Using property setter instead of set_language()
        return parser

    def generate_file_tree(self, path):
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
                ret += self.generate_file_tree(item_path)
            elif item_path.endswith(self.file_extension):
                ret.append(item_path)

        return ret

    def get_method_name(self, node: tree_sitter.Node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None

    def generate_doc(self, ts: tree_sitter.Node, file_bytes):
        source = file_bytes[ts.start_byte:ts.end_byte].decode('utf-8')
        print(source)
        response = self.client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "system", "content": f"""
    Your task is to generate a doc string along with definitions for this {ts.type}
                """},
                {"role": "user", "content": source},
            ]
        )
        print(self.get_method_name(ts), response.output_text)

    def generate_methods(self, ts: tree_sitter.Node, file_bytes, indt: str = ""):
        for node in ts.children:
            print(indt, node.type)
            if node.type == 'function_definition':
                self.generate_doc(node, file_bytes)

            if node.type == 'class_definition':
                self.generate_doc(node, file_bytes)
                self.generate_methods(node, file_bytes, indt + '---')

    def analyze_file(self, path):
        with open(path, 'r') as file:
            bts = file.read().encode()
            file_tree = self.parser.parse(bts)

            self.generate_methods(file_tree.root_node, bts, "")

    def run(self, project_dir=None):
        if project_dir is None:
            project_dir = os.getcwd()

        files = self.generate_file_tree(project_dir)

        print(files)

        for f in files:
            self.analyze_file(f)


class PythonAnalyzer(CodeAnalyzer):
    def __init__(self):
        super().__init__(tspython, 'python', '.py')


def main():
    agp = argparse.ArgumentParser()
    agp.add_argument(
        '--dir',
        default=os.getcwd(),
        help="Project repository directory",
    )
    args = agp.parse_args()

    analyzer = PythonAnalyzer()
    analyzer.run(args.dir)


if __name__ == '__main__':
    main()
