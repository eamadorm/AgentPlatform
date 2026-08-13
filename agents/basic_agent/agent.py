from google.adk.agents.llm_agent import Agent
from google.adk.planners import BuiltInPlanner
from vertexai.agent_engines import AdkApp
from google.adk.models import Gemini
from google.genai.types import (
    GenerateContentConfig,
    HttpRetryOptions,
    ModelArmorConfig,
    ThinkingConfig,
    ThinkingLevel,
    ToolConfig,
    FunctionCallingConfig,
)
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers

# Initialize Cloud Monitoring Exporters for Metrics
gcp_exporters = get_gcp_exporters(enable_cloud_metrics=True)
maybe_set_otel_providers([gcp_exporters])

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

import json
from loguru import logger
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

# 1. Configure Loguru to use GCP Cloud Logging
try:
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client, name="agent_tokens")
    logger.add(handler, format="{message}", level="INFO")
    logger.info("Loguru GCP Handler successfully attached.")
except Exception as e:
    print(f"Failed to attach GCP Logging handler: {e}")

# 2. Create the callback that extracts tokens from each model response
from opentelemetry import trace

def log_llm_tokens(callback_context, llm_response) -> None:
    try:
        if llm_response and llm_response.usage_metadata:
            in_tokens = llm_response.usage_metadata.prompt_token_count or 0
            out_tokens = llm_response.usage_metadata.candidates_token_count or 0
            model = getattr(llm_response, 'model_version', 'gemini-model')
            try:
                session_id = callback_context.session.id
            except Exception:
                session_id = "unknown"
                
            # Extraer Trace ID y Span ID de OpenTelemetry para vincular con BigQuery / Cloud Storage
            span_context = trace.get_current_span().get_span_context()
            trace_id = format(span_context.trace_id, '032x') if span_context.is_valid else None
            span_id = format(span_context.span_id, '016x') if span_context.is_valid else None
            
            # Log as a JSON string so Cloud Logging / BigQuery can parse it cleanly
            payload = json.dumps({
                "event": "llm_usage",
                "model": model,
                "session_id": session_id,
                "trace_id": trace_id,
                "span_id": span_id,
                "input_tokens": in_tokens,
                "output_tokens": out_tokens,
                "total_tokens": in_tokens + out_tokens
            })
            logger.info(payload)
    except Exception as e:
        logger.error(f"Error logging tokens: {e}")

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
    generate_content_config=GenerateContentConfig(
                temperature=0.5,
                top_p=0.95,
                top_k=40,
                max_output_tokens=10_000,
                seed=1080,
                # model_armor_config=ModelArmorConfig(
                #     prompt_template_name=(
                #         f"projects/{self.gcp_config.PROJECT_ID}/locations/"
                #         f"{self.gcp_config.REGION}/templates/"
                #         f"{self.agent_config.MODEL_ARMOR_TEMPLATE_ID}"
                #     ),
                #     response_template_name=(
                #         f"projects/{self.gcp_config.PROJECT_ID}/locations/"
                #         f"{self.gcp_config.REGION}/templates/"
                #         f"{self.agent_config.MODEL_ARMOR_TEMPLATE_ID}"
                #     ),
                # )
               
                tool_config=ToolConfig(
                    function_calling_config=FunctionCallingConfig(mode="AUTO")
                ),
                # thinking_config=ThinkingConfig(
                #     # thinking_budget=2000, # in tokens, for models 2.5 or lower
                #     thinking_level=ThinkingLevel.MINIMAL, # for models above 3.x
                # ),
    ),
    after_model_callback=log_llm_tokens,
)

adk_app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)