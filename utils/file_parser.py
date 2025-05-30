import os

import tree_sitter
from openai import OpenAI

from docgen.generators import (ParsedFunc, generate_file_documentation,
                               generate_method_documentation)
from llms import OpenAIClient
from models import Node, ProjectKnowledgeBase
from utils.helper import get_lang_conf_for_file
from utils.lang_conf import BaseLangConf
from utils.spinner import Spinner


class FileParser():
    file = None
    file_bytes: bytes = None
    tree: tree_sitter.Tree = None
    lang_conf: BaseLangConf = None
    lang: str = 'python'
    client: OpenAI = None

    file_ref: Node = None
    nodes: list[Node] = None

    def __init__(self, project: ProjectKnowledgeBase, path: str, project_dir: str = ""):
        self.project_dir = project_dir
        self.full_path = path
        self.path = path.replace(project_dir, "")
        self.parser, self.lang_conf, self.lang, = get_lang_conf_for_file(path)
        self.client = OpenAIClient()

        self.project = project

        self.nodes = []
        # TODO: TEMP -> Only generate file_ref config if necessary
        # Use git diffs later
        id = f"{project.name}:{self.path}"
        if project.nodes.get(id, None) is None:
            self.file_ref = Node(
                gid=id,
                identifier=self.path,
                file=self.path,
                full_path=self.path,
                path=self.path,

                node_type="file",
            )
            project.nodes[self.file_ref.gid] = self.file_ref
        else:
            self.file_ref = project.nodes[id]

    def analyze_file(self):
        with open(self.full_path, 'rb') as file:
            self.file = file
            self.file_bytes = file.read()
            self.tree = self.parser.parse(self.file_bytes)
            self.generate_tags(self.tree.root_node)
            self.generate_file_doc()

    def generate_method_doc(self, node: tree_sitter.Node):
        source = node.text.decode('utf-8')
        id = self.lang_conf.generateIdentifier(
            self.project, self.path, node)
        if self.project.nodes.get(id, None) is not None:
            self.nodes.append(self.project.nodes.get(id))
            return
        s = Spinner(
            f"Generating docs for {self.path} -> {self.lang_conf.getMethodName(node)}")
        doc = generate_method_documentation(ParsedFunc(
            name=self.lang_conf.getMethodName(node),
            source=source,
            lang=self.lang))
        saved_node = Node(
            gid=id,
            identifier=self.lang_conf.getMethodName(node),
            file=self.path,
            path=self.lang_conf.generateNodePath(node),
            node_type=node.type,
            short_doc=doc
        )

        self.nodes.append(saved_node)
        self.project.nodes[saved_node.gid] = saved_node

        s.done()

    def generate_tags(self, root: tree_sitter.Node):
        for node in root.children:
            if self.lang_conf.isDocNeeded(node):
                self.generate_method_doc(node)
            self.generate_tags(node)

    def generate_file_doc(self):
        s = Spinner(f"Generating docs for {self.path}")
        self.file_ref.short_doc = generate_file_documentation(
            self.lang, os.path.basename(self.full_path), self.path,
            [node.short_doc for node in self.nodes]
        )
        s.done()
