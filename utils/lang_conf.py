import tree_sitter
import os

from models import ProjectKnowledgeBase


class BaseLangConf():
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        raise NotImplementedError()

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        raise NotImplementedError()

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
        return node.type in ['function_definition', 'class_definition']

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
      

class JavaScriptLangConf(BaseLangConf):
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        return node.type in ['function_declaration', 'method_definition', 'class_declaration']

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        if node.type == 'function_declaration':
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode()
        elif node.type == 'method_definition':
            for child in node.children:
                if child.type == 'property_identifier':
                    return child.text.decode()
        elif node.type == 'class_declaration':
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode()
        return None


class CppLangConf(BaseLangConf):
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        return node.type in ['function_definition', 'class_specifier']

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        if node.type == 'function_definition':
            # Look for declarator -> function_declarator -> identifier
            for child in node.children:
                if child.type == 'declarator':
                    for subchild in child.children:
                        if subchild.type == 'function_declarator':
                            for id_child in subchild.children:
                                if id_child.type == 'identifier':
                                    return id_child.text.decode()
        elif node.type == 'class_specifier':
            for child in node.children:
                if child.type == 'type_identifier':
                    return child.text.decode()
        return None


class GoLangConf(BaseLangConf):
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        return node.type in ['function_declaration', 'method_declaration', 'type_declaration']

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        if node.type in ['function_declaration', 'method_declaration']:
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode()
        elif node.type == 'type_declaration':
            for child in node.children:
                if child.type == 'type_spec':
                    for subchild in child.children:
                        if subchild.type == 'type_identifier':
                            return subchild.text.decode()
        return None


class RustLangConf(BaseLangConf):
    @classmethod
    def isDocNeeded(cls, node: tree_sitter.Node):
        return node.type in ['function_item', 'impl_item', 'trait_item', 'struct_item']

    @classmethod
    def getMethodName(cls, node: tree_sitter.Node):
        if node.type == 'function_item':
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode()
        elif node.type in ['impl_item', 'trait_item', 'struct_item']:
            for child in node.children:
                if child.type == 'type_identifier':
                    return child.text.decode()
        return None


def get_lang_conf_for_file(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.py':
        return PythonLangConf
    elif ext == '.js':
        return JavaScriptLangConf
    elif ext in ['.cpp', '.hpp', '.cc', '.cxx']:
        return CppLangConf
    elif ext == '.go':
        return GoLangConf
    elif ext == '.rs':
        return RustLangConf
    else:
        raise ValueError(f"Unsupported file type: {ext}")

