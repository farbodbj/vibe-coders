import os
import fnmatch

def load_patterns(project_dir) -> list[str]:
    """
        Load and parse .gitignore patterns
    """
    gitignore_path = os.path.join(project_dir, '.gitignore')

    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    patterns.append(line)
    
    return patterns


def is_ignored(path: str, patterns: list[str]) -> bool:
    """
        Check if a path should be ignored based on .gitignore patterns
    """
    
    # Normalize path separators for cross-platform compatibility
    path = path.replace(os.sep, '/')
    
    for pattern in patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            # Check if any parent directory matches
            dir_pattern = pattern.rstrip('/')
            path_parts = path.split('/')
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[:i+1])
                if fnmatch.fnmatch(partial_path, dir_pattern):
                    return True
        else:
            # Handle file patterns
            if fnmatch.fnmatch(path, pattern):
                return True
            
            # Also check if any parent directory matches the pattern
            path_parts = path.split('/')
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[:i+1])
                if fnmatch.fnmatch(partial_path, pattern):
                    return True

    return False


if __name__ == "__main__":

    patterns = load_patterns(".")

    isit = is_ignored(
        path = "deploy/Dockerfile",
        patterns = patterns
    )
    print(isit)
