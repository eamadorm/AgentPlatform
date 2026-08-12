from google.adk.agents.llm_agent import Agent
from google.adk.models import Gemini
from google.genai.types import (
    GenerateContentConfig,
    HttpRetryOptions,
    ModelArmorConfig,
    ThinkingConfig,
    ToolConfig,
    FunctionCallingConfig,
)
# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model=Gemini(
        model_name="gemini-2.5-flash-lite",
        # Google ADK uses Google GenAI Client: https://github.com/google/adk-python/blob/v2.6.3/src/google/adk/models/google_llm.py#L343
        # Check client parameters here: # Check available parameters here: https://github.com/googleapis/python-genai/blob/main/google/genai/client.py#L257
        client_kwargs = { 
            "enterprise": True, # To use Agent Platform endpoints
            "location": "us-central1", # location to send API request, useful for data sovereignty    
        },
        retry_options=HttpRetryOptions(
            attempts=3,
            initial_delay=5.0, # seconds
            exp_base=2.0, # seconds
            max_delay=30.0, # seconds
        ),
    ),
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)