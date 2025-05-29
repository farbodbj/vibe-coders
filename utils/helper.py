import os
import tree_sitter
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_cpp
import tree_sitter_go
import tree_sitter_rust
from typing import Dict, Type
from tree_sitter import Language
from utils.lang_conf import (
    BaseLangConf,
    PythonLangConf,
    JavaScriptLangConf,
    CppLangConf,
    GoLangConf,
    RustLangConf
)


def initialize_languages() -> Dict[str, Language]:
    """Initialize and return all language parsers"""
    try:
        languages = {
            'python': Language(tree_sitter_python.language()),
            'javascript': Language(tree_sitter_javascript.language()),
            'cpp': Language(tree_sitter_cpp.language()),
            'go': Language(tree_sitter_go.language()),
            'rust': Language(tree_sitter_rust.language())
        }
        return languages
    except Exception as e:
        raise ImportError(
            "Could not load language parsers. Please install the required packages:\n"
            "pip install tree-sitter-python tree-sitter-javascript tree-sitter-cpp "
            "tree-sitter-go tree-sitter-rust"
        ) from e


def get_language_map() -> Dict[str, Language]:
    """Return mapping of file extensions to language parsers"""
    languages = initialize_languages()
    return {
        '.py': languages['python'],
        '.js': languages['javascript'],
        '.cpp': languages['cpp'],
        '.hpp': languages['cpp'],
        '.cc': languages['cpp'],
        '.cxx': languages['cpp'],
        '.go': languages['go'],
        '.rs': languages['rust']
    }


def get_lang_conf_for_file(file_path: str) -> Type[BaseLangConf]:
    """Return the appropriate language configuration class for a file"""
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


def create_parser(file_path: str, language_map: Dict[str, Language]) -> tree_sitter.Parser:
    """Create and return a configured parser for the given file"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in language_map:
        raise ValueError(f"Unsupported file extension: {ext}")
    return tree_sitter.Parser(language=language_map[ext])


def is_supported_file(file_path):
    """Check if file has a supported extension"""
    supported_extensions = {
        '.py',  # Python
        '.cpp', '.h', '.hpp', '.c',  # C/C++
        '.go',   # Go
        '.js', '.ts', '.jsx', '.tsx',  # JavaScript/TypeScript
        '.rs',   # Rust
        '.java', # Java
        '.kt',   # Kotlin
        '.swift' # Swift
    }
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_extensions
