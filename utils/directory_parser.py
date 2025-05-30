
import os

import gitignore
from docgen.generators import (generate_directory_documentation,
                               generate_markdown_directory_documentation)
from models import Node, ProjectKnowledgeBase
from utils.helper import get_lang_conf_for_file
from utils.spinner import Spinner


def parse_dir(
    path: str, project: ProjectKnowledgeBase,
    project_dir: str, gitignore_patterns: list[str],
    generate_readme_files: bool = True
):
    # print("Generating docs for", path)
    try:
        items = os.listdir(path)
    except OSError as e:
        print(f"Error reading directory {path}: {e}")
        return

    subsections = []
    langs = set()

    for i, item in enumerate(items):
        if gitignore.is_ignored(item, gitignore_patterns):
            continue

        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            # print("Checking dir", item)
            parse_dir(
                path=full_path, project=project, project_dir=project_dir,
                gitignore_patterns=gitignore_patterns,
                generate_readme_files=generate_readme_files,
            )
            subsections.append(
                (f"{project.name}:{item.replace(project_dir, '')}", item)
            )
        else:
            try:
                langs.add(get_lang_conf_for_file(item)[2])
                subsections.append(
                    (f"{project.name}:{item.replace(project_dir, '')}", item)
                )
            except ValueError as e:
                pass

    relp = path.replace(project_dir, '')

    s = Spinner(f"Generating docs for {relp} directory ")
    doc = generate_directory_documentation(
        langs, path,
        [project.nodes[item].short_doc for item, p in subsections]
    )

    # if relp != '':  # Main project directory, use different function?
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
            [project.nodes[item].short_doc for item, p in subsections]
        )
        with open(os.path.join(path, 'README.md'), 'w') as md_file:
            # print(os.path.join(path, 'README.md'))
            md_file.write(mddoc)

            for id, p in subsections:
                if os.path.isdir(p):
                    file_md = f"## [[{project.nodes[id].path}]] \n"
                    file_md += project.nodes[id].short_doc
                    file_md += "\n\n"
                    md_file.write(file_md)
                    continue

                file_md = f"## [[{project.nodes[id].path}]] \n"
                file_md += project.nodes[id].short_doc
                file_md += "\n\n"
                for key, n in project.nodes.items():
                    if key == id:
                        continue
                    if key.startswith(id):
                        # file_md += f'* {n.path}\n\n'
                        v = '\n'.join(
                            ["\t" + x for x in n.short_doc.split('\n')])
                        file_md += f'{v}\n\n'
                file_md += "\n\n"
                md_file.write(file_md)

    s.done()
