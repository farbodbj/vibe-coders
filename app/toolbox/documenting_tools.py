from langchain.tools import tool
from langchain_openai.chat_models import ChatOpenAI
import tree_sitter

class DocGen:
    def __init__(self, llm: ChatOpenAI):
        self._llm = llm
        
        
    def _generate_doc(self, node_source: str, node_name: str):
        prompt = f'''Document the function {node_name} in detail, including its purpose, input parameters, output values, and any exceptions it may throw.
        Provide clear examples and usage instructions to help developers understand how to use the function effectively.
        
        function body: {node_source}
        '''
        return self._llm.invoke(
            input=prompt
        ).content
        
        
    def _get_method_name(node: tree_sitter.Node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None


    def generate_doc(self, ts: tree_sitter.Node, file_bytes)->str:
        method_source = file_bytes[ts.start_byte:ts.end_byte].decode('utf-8')  
        method_name = self._get_method_name(ts)
        return self._generate_doc(method_name, method_source)
    

def generate_method(ts: tree_sitter.Node, file_bytes, indt: str = ""):
    for node in ts.children:
        if node.type == 'function_definition':
            return generate_doc(node, file_bytes)
        # if node.type == 'class_definition':
        #     return generate_doc(node, file_bytes)



@tool
def generate_file_documentation(file_path: str):
    pass

@tool
def generate_directory_documentation():
    pass

@tool
def generate_project_documentation():
    pass
