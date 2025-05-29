from langchain.agents import initialize_agent, AgentType
from llms import openai_llm

class ChainFactory():
    def build(self):
        return initialize_agent(
            tools=[],
            llm=openai_llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            max_iterations=15, # 15 is the default value, i have set the value here for later possible changes
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={}
        )