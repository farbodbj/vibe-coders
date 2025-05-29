import tree_sitter
import tree_sitter_python as tspython
from lang_conf import BaseLangConf, PythonLangConf
from openai import OpenAI

lang = tree_sitter.Language(tspython.language())
parser = tree_sitter.Parser(lang)

client = OpenAI(
    base_url="https://api.metisai.ir/openai/v1"
)


class FileParser():
    file = None
    file_bytes: bytes = None
    tree: tree_sitter.Tree = None
    lang_conf: BaseLangConf = None

    def __init__(self, path):
        self.path = path
        self.parser = parser
        self.lang_conf = PythonLangConf

    def analyze_file(self):
        with open(self.path) as file:
            self.file = file
            self.file_bytes = file.read().encode()
            self.tree = self.parser.parse(self.file_bytes)

            self.generate_tags(self.tree.root_node)

    def generate_method_doc(self, node: tree_sitter.Node):
        source = self.file_bytes[node.start_byte:node.end_byte].decode('utf-8')
        print(source)
        print(node.text.decode('utf-8'))
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {"role": "system", "content": f"""
            Your task is to generate a doc string along with definitions for this {node.type}
                        """},
                {"role": "user", "content": source},
            ]
        )
        print(self.lang_conf.getMethodName(node), response.output_text)

    def generate_tags(self, root: tree_sitter.Node):
        for node in root.children():
            if self.lang_conf.isDocNeeded(node):
                self.generate_method_doc(node)
