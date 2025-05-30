
import os

import gitignore
from docgen.generators import (generate_directory_documentation,
                               generate_markdown_directory_documentation)
from models import Node, ProjectKnowledgeBase
from utils.helper import get_lang_conf_for_file


def parse_dir(
    path: str, project: ProjectKnowledgeBase,
    project_dir: str, gitignore_patterns: list[str],
    generate_readme_files: bool = True
):
    try:
        items = os.listdir(path)
    except OSError as e:
        print(f"Error reading directory {path}: {e}")
        return

    subsections = []
    langs = set()

    for i, item in enumerate(items):
        print("Generating docs for ", item,
              gitignore.is_ignored(item, gitignore_patterns))
        if gitignore.is_ignored(item, gitignore_patterns):
            continue

        if os.path.isdir(item):
            parse_dir(
                path=item, project=project, project_dir=project_dir,
                gitignore_patterns=gitignore_patterns,
                generate_readme_files=generate_readme_files,
            )
            subsections.append(
                f"{project.name}:{item.replace(project_dir, '')}"
            )
        else:
            try:
                langs.add(get_lang_conf_for_file(item)[2])
                subsections.append(
                    f"{project.name}:{item.replace(project_dir, '')}"
                )
            except ValueError as e:
                pass

    doc = generate_directory_documentation(
        langs, path,
        [project.nodes[item].short_doc for item in subsections]
    )

    relp = path.replace(project_dir, '')

    if relp != '':  # Main project directory, use different function?
        node = Node(
            gid=f"{project.name}:{relp}",
            identifier=relp,
            file=relp,
            full_path=relp,
            path=relp,

            node_type="directory",
            short_doc=doc,
        )
        project.nodes[node.gid] = node

    if generate_readme_files:
        mddoc = generate_markdown_directory_documentation(
            langs, path,
            [project.nodes[item].short_doc for item in subsections]
        )
        with open(os.path.join(path, 'README.md'), 'a') as md_file:
            md_file.write(mddoc)
