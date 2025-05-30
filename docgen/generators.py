from textwrap import dedent
from typing import List

import dotenv
from pydantic import BaseModel

from llms import MEDIUM_MODEL, SMALL_MODEL, OpenAIClient

dotenv.load_dotenv()

client = OpenAIClient()


class ParsedFunc(BaseModel):
    name: str
    source: str
    lang: str


def generate_method_documentation(parsed_func: ParsedFunc) -> str:
    response = client.chat.completions.create(
        model=SMALL_MODEL,
        messages=[
            {"role": "system", "content": dedent(f"""
                You're an elite software engineer with great knowledge in {parsed_func.lang} programming language, you will be given
                a function name and body and you're tasked with generating a short documentation for it formatted as follows:

                * <function name>: <brief description of the function>
                    * arg_1: <short description of arg 1>
                    * arg_2: <short description of arg 2>
                    ...

                function name: {parsed_func.name}
                function source: {parsed_func.source}
                """)},
            {"role": "user", "content": "formatted documentation: "},
        ]
    )
    return response.choices[0].message.content


def generate_file_documentation(language: str, filename: str, filepath: str, function_descriptions: List[str]) -> str:
    MAX_SUPPORTED_FUNCTIONS = 100
    response = client.chat.completions.create(
        model=MEDIUM_MODEL,
        messages=[
            {"role": "system", "content": dedent(f"""
                You're an elite software engineer with great knowledge in {language} programming language, you are tasked to 
                thoroughly inspect a list of documentations of functions implemented in a file and then summarizing the functionalities,
                components or a possible logical unit implemented in that file, your description should give the reader 
                a fairly concise view of what is going inside the file. Avoid being wordy or writing too long descriptions. 
                You output format should be as follows:

                * <filename>: <description of the file in several sentences>

                filename: {filename}
                file path: {filepath}
                function description list: {function_descriptions[:MAX_SUPPORTED_FUNCTIONS]}"""
                                                 )},
            {"role": "user", "content": "formatted file documentation: "},
        ]
    )
    return response.choices[0].message.content


def generate_directory_documentation(languages: list[str], directory_path: str, file_descriptions: List[str]) -> str:
    MAX_SUPPORTED_FILES = 50
    response = client.chat.completions.create(
        model=MEDIUM_MODEL,
        messages=[
            {"role": "system", "content": dedent(f"""
            You're an elite software engineer with great knowledge in {languages} programming language, you are tasked to
            thoroughly inspect a list of file descriptions from a directory and then summarizing the overall purpose,
            architecture, and main components implemented in that directory. Your description should give the reader
            a comprehensive yet concise view of what this directory contains and its role in the larger codebase.
            Avoid being wordy or writing too long descriptions.
            Your output format should be as follows:
            * <directory_name>: <description of the directory in several sentences>

            directory path: {directory_path}
            file description list: {file_descriptions[:MAX_SUPPORTED_FILES]}"""
                                                 )},
            {"role": "user", "content": "formatted directory documentation: "},
        ]
    )
    return response.choices[0].message.content


def generate_markdown_directory_documentation(languages: list[str], directory_path: str, file_descriptions: List[str]) -> str:
    MAX_SUPPORTED_FILES = 50
    response = client.chat.completions.create(
        model=MEDIUM_MODEL,
        messages=[
            {"role": "system", "content": dedent(f"""
            You're an elite software engineer with great knowledge in {languages} programming language, you are tasked to
            thoroughly inspect a list of file descriptions from a directory and then summarizing the overall purpose,
            architecture, and main components implemented in that directory. Your description should give the reader
            a comprehensive yet concise view of what this directory contains and its role in the larger codebase.
            Avoid being wordy or writing too long descriptions.
            All your outputs will have markdown(.md) format
            Your output format should be as follows:
            ```

            # <directory_name>
            <description of the directory in several sentences>

            ## <filename or subdirectory name>
            <description of file or breif description of the subdirectory>

            ```

            -- directory path: 
            {directory_path}
            -- file description list: 
            {file_descriptions[:MAX_SUPPORTED_FILES]}"""
                                                 )},
            {"role": "user", "content": "formatted directory documentation: "},
        ]
    )
    return response.choices[0].message.content

