import os
import dotenv
from langchain_openai.chat_models import ChatOpenAI
import tree_sitter
import tree_sitter_python as tspython

dotenv.load_dotenv()


class DocGen:

    def __init__(self, llm: ChatOpenAI):
        self._llm = llm
        self.func_to_doc = {}


    def _get_method_name(node: tree_sitter.Node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None


    def generate_doc(self, ts: tree_sitter.Node, file_bytes)->str:
        method_source = file_bytes[ts.start_byte:ts.end_byte].decode('utf-8')
        method_name = self._get_method_name(ts)

        prompt = f'''Document the function {method_name} in detail, including its purpose, input parameters, output values, and any exceptions it may throw.
        Provide clear examples and usage instructions to help developers understand how to use the function effectively.

        function body: {method_source}
        '''
        return self._llm.invoke(
            input=prompt
        ).content


    def generate_method(self, ts: tree_sitter.Node, file_bytes):
        for node in ts.children:
            if node.type == 'function_definition':
                name = self._get_method_name(node)
                doc = self.generate_doc(node, file_bytes)
                self.func_to_doc[name] = doc
            # if node.type == 'class_definition':
            #     return generate_doc(node, file_bytes)


class Doc:

    def __init__(self, llm: ChatOpenAI) -> None:
        self._llm = llm


    def _get_method_name(self, node: tree_sitter.Node) -> str|None:
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None


    def generate_method_doc(self, name: str, node: tree_sitter.Node, bytes: bytes) -> str:
        code = bytes[node.start_byte:node.end_byte].decode('utf-8')

        prompt = f"""
            Document the function "{name}", including its purpose, input parameters, output values, and any exceptions it may throw.
            Provide clear examples and usage instructions to help developers understand how to use the function effectively.
            function body: ```{code}```
            Documentation:
        """
        content = self._llm.invoke(
            input = prompt
        ).content
        print(f"Generated documentation for '{name}'.")
        return content


    def generate_methods_doc(self, tree: tree_sitter.Tree, bytes: bytes) -> dict:
        func_to_doc = {}
        root_node = tree.root_node  # Start from the root node

        for node in root_node.children:
            if node.type == 'function_definition':
                name = self._get_method_name(node)
                doc  = self.generate_method_doc(name, node, bytes)
                func_to_doc[name] = doc

        return func_to_doc


    def generate_file_doc(self, func_to_doc: dict) -> str:
        prompt = f"""
            You are given a dictionary of file documentations for a single file. You are to write a documentation for it.

            Instructions:
                1. Provide an overview of the file's purpose and main functionality
                2. Describe the key classes, functions, and their relationships
                3. Explain the overall architecture and design patterns used
                4. Include usage examples if applicable

            Function documentation: ```{func_to_doc}```
            Documentation:
        """
        return self._llm.invoke(
            input = prompt
        ).content


    def analyze_file(self, path: str, language: str):
        # Set code language
        lang = None
        if language == "python":
            lang = tree_sitter.Language(tspython.language())

        # Define parser object
        parser = tree_sitter.Parser(lang)

        with open(path, 'r') as file:
            bytes = file.read().encode()
            tree = parser.parse(bytes)

        func_to_doc = self.generate_methods_doc(tree, bytes)
        return self.generate_file_doc(func_to_doc)



if __name__ == "__main__":
    llm = ChatOpenAI(
        temperature = float(os.getenv("OPENAI_MODEL_TEMPERATURE")),
        model = os.getenv("OPENAI_MODEL"),
        base_url = os.getenv("OPENAI_BASE_URL"),
        api_key = os.getenv("OPENAI_API_KEY"),
    )

    doc = Doc(llm)
    doc = doc.analyze_file("tree_sitter_sample.py", "python")
    print(doc)
