import tree_sitter


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
