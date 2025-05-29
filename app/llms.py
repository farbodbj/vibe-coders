from toolbox.documenting_tools import DocGen, generate_directory_documentation, generate_file_documentation
from langchain_openai import ChatOpenAI
import os

openai_llm = ChatOpenAI(
        temperature=float(os.getenv("TEMPERATURE")), # temp of 0 will cause model to never correct mistakes 
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
