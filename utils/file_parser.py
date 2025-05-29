from typing import Optional

import tree_sitter
from openai import OpenAI

from models import Node, ProjectKnowledgeBase
from utils.helper import get_lang_conf_for_file
from utils.lang_conf import BaseLangConf


class OpenAIClient:
    _client: Optional[OpenAI] = None

    def __new__(cls, *args, **kwargs):
        if cls._client:
            return cls._client
        cls._client = OpenAI(
            base_url="https://api.metisai.ir/openai/v1"
        )
        return cls._client


class FileParser():
    file = None
    file_bytes: bytes = None
    tree: tree_sitter.Tree = None
    lang_conf: BaseLangConf = None
    client: OpenAI = None

    file_ref: Node = None

    def __init__(self, project: ProjectKnowledgeBase, path: str, project_dir: str = ""):
        self.project_dir = project_dir
        self.full_path = path
        self.path = path.replace(project_dir, "")
        self.parser, self.lang_conf, = get_lang_conf_for_file(path)
        self.client = OpenAIClient()

        self.project = project

        self.file_ref = Node(
            gid=f"{project.name}:{path}",
            identifier=path,
            file=path,
            full_path=path,
            path=path,

            node_type="file",
        )
        project.nodes[self.file_ref.gid] = self.file_ref

    def analyze_file(self):
        with open(self.full_path, 'rb') as file:
            self.file = file
            self.file_bytes = file.read()
            self.tree = self.parser.parse(self.file_bytes)
            self.generate_tags(self.tree.root_node)

    def generate_method_doc(self, node: tree_sitter.Node):
        source = node.text.decode('utf-8')
        response = self.client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {"role": "system", "content": f"""
            Your task is to generate a doc string along with definitions for this {node.type}
                        """},
                {"role": "user", "content": source},
            ]
        )

        saved_node = Node(
            gid=self.lang_conf.generateIdentifier(
                self.project, self.path, node),
            identifier=self.lang_conf.getMethodName(node),
            file=self.path,
            path=self.lang_conf.generateNodePath(node),
            node_type=node.type,
            short_doc=response.output_text
        )

        self.project.nodes[saved_node.gid] = saved_node

    def generate_tags(self, root: tree_sitter.Node):
        for node in root.children:
            if self.lang_conf.isDocNeeded(node):
                self.generate_method_doc(node)
            self.generate_tags(node)
