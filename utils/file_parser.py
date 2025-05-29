from tree_sitter import Parser
from openai import OpenAI
import tree_sitter
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_cpp
import tree_sitter_go
import tree_sitter_rust
from typing import Optional
from utils.helper import get_language_map, get_lang_conf_for_file, create_parser

LANGUAGE_MAP = get_language_map()


class OpenAIClient:
    _client: Optional[OpenAI] = None

    def __new__(cls, *args, **kwargs):
        if cls._client:
            return cls._client
        cls._client = OpenAI(
            base_url="https://api.metisai.ir/openai/v1"
        )
        return cls._client


class FileParser:
    def __init__(self, path: str):
        self.path = path
        self.lang_conf = get_lang_conf_for_file(path)
        self.parser = create_parser(path, LANGUAGE_MAP)
        self.client = OpenAIClient()

    def analyze_file(self):
        with open(self.path, 'rb') as file:
            self.file_bytes = file.read()
            self.tree = self.parser.parse(self.file_bytes)
            self.generate_tags(self.tree.root_node)

    def generate_method_doc(self, node: tree_sitter.Node):
        source = node.text.decode('utf-8')
        response = self.client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {"role": "system", "content": f"""
            Your task is to generate a doc string along with definitions  this {node.type}
                        """},
                {"role": "user", "content": source},
            ]
        )
        print(self.lang_conf.getMethodName(node), response.output_text)

    def generate_tags(self, root: tree_sitter.Node):
        for node in root.children:
            if self.lang_conf.isDocNeeded(node):
                self.generate_method_doc(node)
            self.generate_tags(node)
