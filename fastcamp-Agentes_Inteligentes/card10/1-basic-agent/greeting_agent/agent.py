from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 

MODEL_GEMINI = "gemini-2.0-flash"
MODEL_GPT = "openai/gpt-4.1-nano-2025-04-14"
MODEL_CLAUDE = "anthropic/claude-haiku-4-5-20251001"

root_agent = Agent(
    name="greeting_agent",
    model=LiteLlm(model=MODEL_GPT),
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user. 
    Ask for the user's name and greet them by name.
    """,
    
)
