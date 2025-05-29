from langchain_openai import ChatOpenAI
import os
from langchain.agents import initialize_agent, AgentType
from toolbox.documenting_tools import DocGen, generate_directory_documentation, generate_file_documentation

llm = ChatOpenAI(
        temperature=float(os.getenv("TEMPERATURE")), # temp of 0 will cause model to never correct mistakes 
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )




class ChainFactory():
    def build(self):
        return initialize_agent(
            tools=[],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            max_iterations=15, # 15 is the default value, i have set the value here for later possible changes
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={}
        )