import tree_sitter

from models import ProjectKnowledgeBase


class BaseLangConf():
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        raise NotImplementedError()

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None

    @classmethod
    def generateIdentifier(cls, project: ProjectKnowledgeBase, node: tree_sitter.Node):
        raise NotImplementedError()

    @classmethod
    def isWorthyScope(cls, project: ProjectKnowledgeBase, node: tree_sitter.Node):
        raise NotImplementedError()

    @classmethod
    def generateNodePath(cls, node: tree_sitter.Node):
        raise NotImplementedError()


class PythonLangConf(BaseLangConf):
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        return node.type == 'function_definition' or node.type == 'class_definition'

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None

    @classmethod
    def generateIdentifier(cls, project: ProjectKnowledgeBase, file_path: str, node: tree_sitter.Node):
        return f"{project.name}:{file_path}:{cls.generateNodePath(node)}"

    @classmethod
    def isWorthyScope(cls, node: tree_sitter.Node):
        return node.type == 'function_definition' or node.type == 'class_definition'

    @classmethod
    def generateNodePath(cls, node: tree_sitter.Node):
        sections = []
        while node:
            if cls.isWorthyScope(node):
                sections.append(cls.getMethodName(node))

            node = node.parent
        return '.'.join(reversed(sections))
