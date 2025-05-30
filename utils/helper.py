import os
from typing import Dict, Type

import tree_sitter
import tree_sitter_cpp
import tree_sitter_go
import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_rust
from tree_sitter import Language

from utils.lang_conf import (BaseLangConf, CppLangConf, GoLangConf,
                             JavaScriptLangConf, PythonLangConf, RustLangConf)


def initialize_languages() -> Dict[str, Language]:
    """Initialize and return all language parsers"""
    try:
        languages = {
            'python': tree_sitter.Parser(Language(tree_sitter_python.language())),
            'javascript': tree_sitter.Parser(Language(tree_sitter_javascript.language())),
            'cpp': tree_sitter.Parser(Language(tree_sitter_cpp.language())),
            'go': tree_sitter.Parser(Language(tree_sitter_go.language())),
            'rust': tree_sitter.Parser(Language(tree_sitter_rust.language()))
        }
        return languages
    except Exception as e:
        raise ImportError(
            "Could not load language parsers. Please install the required packages:\n"
            "pip install tree-sitter-python tree-sitter-javascript tree-sitter-cpp "
            "tree-sitter-go tree-sitter-rust"
        ) from e


languages = initialize_languages()


def get_lang_conf_for_file(file_path: str) -> Type[BaseLangConf]:
    """Return the appropriate language configuration class for a file"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.py':
        return languages['python'], PythonLangConf, 'python',
    elif ext == '.js':
        return languages['javascript'], JavaScriptLangConf, 'javascript',
    elif ext in ['.cpp', '.hpp', '.cc', '.cxx', '.h']:
        return languages['cpp'], CppLangConf, 'C++',
    elif ext == '.go':
        return languages['go'], GoLangConf, 'Go'
    elif ext == '.rs':
        return languages['rust'], RustLangConf, 'Rust'
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
        '.java',  # Java
    }
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_extensions
