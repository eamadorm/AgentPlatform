# AgentPlatform
Different agents deployed in Agent Platform integrating networking and monitoring

## Observability and Telemetry

The system uses the deep integration of **Agent Development Kit (ADK)** with **OpenTelemetry** and Google Cloud Observability to measure, record, and analyze each agent interaction.

> 📚 **Full Setup Guide**: For detailed instructions on how to replicate this setup, required IAM permissions, and architecture details, please refer to the [Observability Setup Guide](file:///workspaces/AgentPlatform/OBSERVABILITY_SETUP.md).

### What is saved and where?

1. **Cloud Trace (Call Cascades and Latencies):**
   - **What it is:** Every time the agent runs, a trace is created that includes spans for LLM calls (`call_llm`), tool execution (`execute_tool`), and agent orchestration (`invoke_agent`).
   - **Where to view it:** In the Google Cloud Console -> **Trace Explorer**.
   - **What it's for:** Identifying bottlenecks and understanding step-by-step how the agent reasons.

2. **Cloud Storage (Multimodal Payloads):**
   - **What it is:** Because Trace and Logging have size limits for text, massive prompts, huge contexts, or multimedia files (images, audio) are saved natively in `.jsonl` format in a bucket.
   - **Where it is:** `gs://host-endava-ge-prod-01-2u00-otel-genai-traces/traces/`
   - **How it interacts:** Cloud Trace knows how to read these files; when you open the trace in the web console, the Trace UI fetches the JSON from this bucket and renders it interactively in the "Input/Output" tab.

3. **Cloud Logging (System Logs):**
   - **What it is:** Traditional Python application logs, Uvicorn (web server) logs, and error events.
   - **Where to view it:** In the Google Cloud Console -> **Logs Explorer**.

### Analytics with BigQuery

To cross-reference information, analyze token usage, and perform massive analytics on the LLM's behavior, we enabled an analytics ecosystem in **BigQuery**.

#### 1. External Table for Prompts and Responses
We created an external table (`multimodal_traces`) in BigQuery that points directly to the JSONL payloads in your Cloud Storage bucket. This allows you to query your conversational history with standard SQL without having to duplicate data.

To explore it, go to the [BigQuery Console](https://console.cloud.google.com/bigquery) and run a query in the `agent_observability` dataset:

```sql
-- Example: Query the contents of the multimodal payloads
SELECT 
  role,
  parts[SAFE_OFFSET(0)].content as message_content
FROM `host-endava-ge-prod-01-2u00.agent_observability.multimodal_traces`
LIMIT 10;
```

> **Note on Log Sinks**: We created a direct Cloud Logging router to BigQuery (`agent_logs_to_bq`) for transactional logs, and the IAM permissions were successfully granted in this project. All standard application logs are now flowing into the `agent_observability` dataset.
