
from langchain_openai.chat_models import ChatOpenAI
import os
from toolbox.documenting_tools import Doc


llm = ChatOpenAI(
        temperature=float(os.getenv("OPENAI_MODEL_TEMPERATURE", "0.1")),
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

doc = Doc(llm)

# Example usage - document current directory
project_path = input("Enter project path (or press Enter for current directory): ").strip()
if not project_path:
    project_path = "."

try:
    # Document the entire project
    project_structure = doc.document_project(project_path)
    print(f"\nDocumentation generated successfully!")
    print(f"Check the README.md files in each directory for the documentation.")
    
except Exception as e:
    print(f"Error: {e}")