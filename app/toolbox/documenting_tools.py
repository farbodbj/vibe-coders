import os
import dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
import tree_sitter
import tree_sitter_python as tspython
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Tuple

dotenv.load_dotenv()

class Doc:
    def __init__(self, llm: ChatOpenAI) -> None:
        self._llm = llm
    
    def _get_parser(self, lang: str) -> tree_sitter.Parser:
        return {
            "python": tree_sitter.Parser(tree_sitter.Language(tspython.language()))
        }.get(lang, None)
    
    def _get_method_name(self, node: tree_sitter.Node) -> str|None:
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None
    
    def generate_method_doc(self, name: str, node: tree_sitter.Node, bytes: bytes) -> str:
        code = bytes[node.start_byte:node.end_byte].decode('utf-8')
        systemp_prompt = dedent(f"""
            Write documentation the following method written including its purpose, input parameters, output values, and any exceptions it may throw.
            Only output the documentation, don't write any code.
            function: 
            {code}
            documentation:
        """)
        response = self._llm.invoke(
            input = [
                SystemMessage(content = systemp_prompt)
            ]
        )
        print(f"Generated documentation for '{name}'.")
        return response.content
    
    def generate_methods_doc(self, walkable: tree_sitter.Tree | tree_sitter.Node, bytes: bytes, func_to_doc: dict = None) -> dict:
        func_to_doc = {} if not func_to_doc else func_to_doc
        root_node = walkable.root_node  if type(walkable) == tree_sitter.Tree else walkable # Start from the root node
        for node in root_node.children:
            if node.type == 'function_definition':
                name = self._get_method_name(node)
                if name:
                    doc = self.generate_method_doc(name, node, bytes)
                    func_to_doc[name] = doc
            if node.type in {'class_definition', 'block'}:
                return self.generate_methods_doc(node, bytes, func_to_doc)
            
        return func_to_doc
    
    def generate_file_doc(self, func_to_doc: dict, file_path: str) -> str:
        prompt = dedent(f"""
            I will provide you with a Python dictionary. The dictionary contains function names as keys and their corresponding 
            docstrings as values. Your task is to:
            1. Parse the dictionary and extract each function's name and docstring.
            2. Format the content into a Markdown file following this structure for each function:
            function_name
            Description: Docstring content (format as readable Markdown)
            3. Combine all entries into a single Markdown document.
            4. Add a title at the top: # Function Documentation
            5. Output the full Markdown text ready to be saved as a .md file.

            Functions and their docstrings: 
            {func_to_doc}
            .md file:
        """)
        return self._llm.invoke(
            input = prompt
        ).content
        
    
    def analyze_file(self, path: str, language: str = "python"):
        # Set code language
        parser = self._get_parser(language)
        if parser is None:
            print(f"Warning: Unsupported language '{language}' for file {path}")
            return None
            
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                bytes_content = content.encode('utf-8')
                tree = parser.parse(bytes_content)
            func_to_doc = self.generate_methods_doc(tree, bytes_content)
            return self.generate_file_doc(func_to_doc, path)
        except Exception as e:
            print(f"Error analyzing file {path}: {e}")
            return None
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a supported code file based on extension"""
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _get_language_from_extension(self, filename: str) -> str:
        """Determine language from file extension"""
        extension_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
        }
        for ext, lang in extension_to_lang.items():
            if filename.endswith(ext):
                return lang
        return 'python'  # default fallback
    
    def analyze_project(self, path: str) -> Dict[str, Dict]:
        """
        Analyze entire project structure and return organized documentation
        Returns: {directory_path: {'files': {file: doc}, 'subdirs': [subdir_names]}}
        """
        if not os.path.isdir(path):
            raise ValueError(f"Directory {path} does not exist!")
        
        project_structure = {}
        
        for root, dirs, files in os.walk(path, followlinks=False):
            # Filter out hidden directories and common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git', 'venv', 'env']]
            
            # Get relative path from project root
            rel_path = os.path.relpath(root, path)
            if rel_path == '.':
                rel_path = ''
            
            # Initialize directory structure
            project_structure[rel_path] = {
                'files': {},
                'subdirs': dirs.copy()
            }
            
            # Process code files in current directory
            code_files = [f for f in files if self._is_code_file(f) and not f.startswith('.')]
            
            for file in code_files:
                file_path = os.path.join(root, file)
                language = self._get_language_from_extension(file)
                print(f"Analyzing: {os.path.join(rel_path, file) if rel_path else file}")
                
                doc = self.analyze_file(file_path, language)
                if doc:
                    project_structure[rel_path]['files'][file] = doc
        
        return project_structure
    
    def generate_directory_summary(self, dir_path: str, files_docs: Dict[str, str], subdirs: List[str]) -> str:
        """Generate a summary for a specific directory"""
        prompt = f"""
            You are documenting a directory: {dir_path if dir_path else 'root directory'}
            
            This directory contains:
            - Files: {list(files_docs.keys()) if files_docs else 'None'}
            - Subdirectories: {subdirs if subdirs else 'None'}
            
            File documentations:
            ```{files_docs}```
            
            Instructions:
                1. Provide a clear overview of what this directory contains and its purpose
                2. Explain how the files in this directory work together
                3. Describe the role of each file briefly
                4. If there are subdirectories, mention their likely purpose based on their names
                5. Keep it concise but informative
                6. Focus on the directory's role in the overall project structure
            
            Directory Summary:
        """
        return self._llm.invoke(input=prompt).content
    
    def create_markdown_documentation(self, project_structure: Dict, project_path: str, output_dir: str = None):
        """
        Create markdown documentation files for the entire project
        """
        if output_dir is None:
            output_dir = project_path
        
        # Process each directory
        for dir_path, content in project_structure.items():
            files_docs = content['files']
            subdirs = content['subdirs']
            
            # Generate directory summary
            summary = self.generate_directory_summary(dir_path, files_docs, subdirs)
            
            # Create markdown content
            markdown_content = self._create_directory_markdown(
                dir_path, summary, files_docs, subdirs
            )
            
            # Determine output file path
            if dir_path == '':
                readme_path = os.path.join(output_dir, 'README.md')
                dir_display_name = "Project Root"
            else:
                dir_output_path = os.path.join(output_dir, dir_path)
                os.makedirs(dir_output_path, exist_ok=True)
                readme_path = os.path.join(dir_output_path, 'README.md')
                dir_display_name = os.path.basename(dir_path) or dir_path
            
            # Write markdown file
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Created documentation: {readme_path}")
    
    def _create_directory_markdown(self, dir_path: str, summary: str, files_docs: Dict[str, str], subdirs: List[str]) -> str:
        """Create markdown content for a directory"""
        dir_name = os.path.basename(dir_path) if dir_path else "Project Root"
        
        markdown = f"# {dir_name}\n\n"
        
        # Add directory summary
        markdown += f"{summary}\n\n"
        
        # Add subdirectories section
        if subdirs:
            markdown += "## Subdirectories\n\n"
            for subdir in sorted(subdirs):
                subdir_path = os.path.join(dir_path, subdir) if dir_path else subdir
                markdown += f"- **[{subdir}]({subdir}/README.md)** - Subdirectory containing related functionality\n"
            markdown += "\n"
        
        # Add files section
        if files_docs:
            markdown += "## Files\n\n"
            for filename, doc in sorted(files_docs.items()):
                markdown += f"### {filename}\n\n"
                markdown += f"{doc}\n\n"
                markdown += "---\n\n"
        
        # Add footer with navigation
        if dir_path:  # Not root directory
            parent_path = os.path.dirname(dir_path)
            if parent_path:
                markdown += f"**Parent Directory:** [../{os.path.basename(parent_path)}](../README.md)\n\n"
            else:
                markdown += f"**Parent Directory:** [Project Root](../README.md)\n\n"
        
        return markdown
    
    def document_project(self, project_path: str, output_dir: str = None):
        """
        Complete workflow to analyze and document an entire project
        """
        print(f"Starting project documentation for: {project_path}")
        
        # Analyze the entire project
        project_structure = self.analyze_project(project_path)
        
        # Create markdown documentation
        self.create_markdown_documentation(project_structure, project_path, output_dir)
        
        print(f"Project documentation completed!")
        return project_structure