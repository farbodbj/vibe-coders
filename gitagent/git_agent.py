import dotenv
dotenv.load_dotenv()
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools import ShellTool
import os
import glob

# Initialize GitHub wrapper and toolkit
github = GitHubAPIWrapper(
    github_repository = "farbodbj/vibe-coders",
    github_app_id = "1340805",
    github_app_private_key = open("vibedocumentor.2025-05-29.private-key.pem", "r").read()
)
toolkit = GitHubToolkit.from_github_api_wrapper(github)

tools = []
for tool in toolkit.get_tools():
    if tool.name == "Create Pull Request":
        tool.name = tool.mode
        tools.append(tool)

git_tool = ShellTool(name="git_terminal")
tools.append(git_tool)

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.1
)

# Create agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Git documentation agent. Your job is to interact with local git repository and:
1. Commit newly created documentation local files to a new branch
2. Push the branch to the repository
3. Create a pull request for the documentation updates

Follow these steps:
1. Create a new branch named 'docs/auto-generated' or similar
2. Add all documentation files (typically .md files) to staging
3. Commit with a clear message about documentation updates
4. Push the new branch to origin
5. Create a pull request with appropriate title and description

Be concise and handle errors gracefully. Use the available GitHub and command-line tools effectively."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Create the agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

class GitDocumentationAgent:
    def __init__(self, repo_owner, repo_name, base_branch="main"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_branch = base_branch
        self.agent_executor = agent_executor
    
    def commit_and_create_pr(self, doc_files_pattern="**/*.md", commit_message="Auto-generated documentation update"):
        """
        Commit documentation files and create a PR
        
        Args:
            doc_files_pattern: Glob pattern for documentation files
            commit_message: Commit message for the documentation update
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"docs/auto-generated-{timestamp}"
        
        # Find documentation files
        doc_files = glob.glob(doc_files_pattern, recursive=True)
        if not doc_files:
            print("No documentation files found to commit")
            return None
        
        print(f"Found {len(doc_files)} documentation files to commit")
        
        # Prepare the instruction for the agent
        instruction = f"""
        Please perform the following git operations for repository {self.repo_owner}/{self.repo_name}:
        
        1. Create a new branch named '{branch_name}' from '{self.base_branch}'
        2. Add and commit these documentation files: {', '.join(doc_files)}
        3. Use commit message: "{commit_message}"
        4. Push the branch '{branch_name}' to origin
        5. Create a pull request from '{branch_name}' to '{self.base_branch}' with:
           - Title: "📚 Auto-generated Documentation Update"
           - Description: "This PR contains automatically generated documentation files.
           
           Files updated:
           {chr(10).join([f'- {file}' for file in doc_files])}
           
           Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        Handle any errors gracefully and provide status updates.
        """
        
        try:
            result = self.agent_executor.invoke({"input": instruction})
            print("Git operations completed successfully!")
            return result
        except Exception as e:
            print(f"Error during git operations: {str(e)}")
            return None
    
    def simple_commit_and_pr(self, files_to_add=None):
        """
        Simplified version that commits all changes and creates PR
        """
        if files_to_add is None:
            files_to_add = "."  # Add all changes
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"docs/update-{timestamp}"
        
        instruction = f"""
        Repository: {self.repo_owner}/{self.repo_name}
        
        Execute these git operations:
        1. Create branch '{branch_name}' from '{self.base_branch}'
        2. Add files: {files_to_add}
        3. Commit with message: "docs: automated documentation update"
        4. Push branch '{branch_name}'
        5. Create PR: '{branch_name}' -> '{self.base_branch}'
           Title: "📚 Documentation Update"
           Description: "Automated documentation generation and update."
        """
        
        return self.agent_executor.invoke({"input": instruction})

# Usage example
def main():
    
    # Initialize the agent
    git_agent = GitDocumentationAgent("farbodbj", "vibe-coders-copy")
    
    # Method 1: Commit specific documentation files
    result = git_agent.commit_and_create_pr(
        doc_files_pattern="**/*.md",
        commit_message="docs: add automated API documentation"
    )
    
    # Method 2: Simple commit all changes
    # result = git_agent.simple_commit_and_pr()
    
    if result:
        print("Documentation committed and PR created successfully!")
        print(f"Result: {result['output']}")
    else:
        print("Failed to complete git operations")

if __name__ == "__main__":
    main()