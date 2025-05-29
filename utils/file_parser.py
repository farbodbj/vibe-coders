import tree_sitter
import tree_sitter_python as tspython
from openai import OpenAI

from models import Node, ProjectKnowledgeBase
from utils.lang_conf import BaseLangConf, PythonLangConf

lang = tree_sitter.Language(tspython.language())
parser = tree_sitter.Parser(lang)


class OpenAIClient():
    _client = None

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

    def __init__(self, project: ProjectKnowledgeBase, path: str):
        self.path = path
        self.parser = parser
        self.lang_conf = PythonLangConf
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
        with open(self.path) as file:
            self.file = file
            self.file_bytes = file.read().encode()
            self.tree = self.parser.parse(self.file_bytes)

            self.generate_tags(self.tree.root_node)

    def generate_method_doc(self, node: tree_sitter.Node):
        # source = self.file_bytes[node.start_byte:node.end_byte].decode('utf-8')
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
