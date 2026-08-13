# Observability and Telemetry Guide: AgentPlatform

This document describes the telemetry architecture of `AgentPlatform`, the manual steps to configure it in new environments, and the required permissions.

---

## 1. Observability Architecture
To deal with Google Cloud's size limitations (for example, the 256 bytes per span attribute limit in Cloud Trace), AgentPlatform uses a multi-product strategy powered by **OpenTelemetry**.

*   **Cloud Trace**: Stores the "Spans" (the waterfalls of how long LLMs, tools, and functions take). This is also where attributes like *used tokens* and the *selected model* reside.
*   **Cloud Storage**: Receives massive texts and multimedia. The entire conversational history and base64 images are exported directly as `.jsonl` files.
*   **Cloud Logging**: Receives the server logs (Uvicorn) and Python transactional events.
*   **BigQuery**: Acts as the cross-analysis engine for all the information (thanks to external tables and Log Sinks).

---

## 2. Required Permissions (IAM)

To replicate or maintain this setup in another project, your user (or Service Account) needs the following roles:

| Component | Required Role | Description |
| :--- | :--- | :--- |
| **Enable APIs** | `roles/serviceusage.serviceUsageAdmin` | Allows enabling the necessary APIs (`bigquery`, `logging`, `trace`, `storage`). |
| **Cloud Storage** | `roles/storage.admin` | Allows creating the bucket to store multimodal traces. |
| **BigQuery** | `roles/bigquery.dataEditor` | Allows creating the dataset and external tables. |
| **Log Sinks** | `roles/logging.configWriter` | **Crucial:** Allows creating log routers from Cloud Logging to BigQuery. (Or you can temporarily use `roles/owner`). |

---

## 3. Step-by-Step Configuration Guide

If you want to set this all up in a completely new project from scratch, these are the automated commands we used.

### Step 3.1: Enable APIs
```bash
gcloud services enable bigquery.googleapis.com cloudtrace.googleapis.com logging.googleapis.com storage.googleapis.com
```

### Step 3.2: Configure Storage (Multimodal Traces)
Create the bucket that will host the JSON files of the chats. **The name must be globally unique**.
```bash
gcloud storage buckets create gs://[YOUR_PROJECT]-otel-genai-traces \
  --project=[YOUR_PROJECT] --location=us-central1
```

### Step 3.3: Configure the Agent (.env)
Make sure the `AgentPlatform` `.env` contains the directive to point to that bucket and use the upload format for traces:
```env
OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK=upload
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT
OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH=gs://[YOUR_PROJECT]-otel-genai-traces/traces
```

### Step 3.4: Analytics in BigQuery
Create a dataset called `agent_observability`.
```bash
bq mk --location=us-central1 -d [YOUR_PROJECT]:agent_observability
```
Create the **External Table** pointing to the bucket. This allows BigQuery to read the `.jsonl` files directly.
```bash
cat << 'EOF' > schema.json
[
  { "name": "trace_id", "type": "STRING" },
  { "name": "span_id", "type": "STRING" },
  { "name": "role", "type": "STRING" },
  { "name": "parts", "type": "RECORD", "mode": "REPEATED", "fields": [
      { "name": "content", "type": "STRING" },
      { "name": "type", "type": "STRING" }
  ] },
  { "name": "finish_reason", "type": "STRING" }
]
EOF

cat << 'EOF' > table_def.json
{
  "ignoreUnknownValues": true,
  "sourceFormat": "NEWLINE_DELIMITED_JSON",
  "sourceUris": [ "gs://[YOUR_PROJECT]-otel-genai-traces/traces/*" ]
}
EOF

bq mk --external_table_definition=table_def.json@schema.json [YOUR_PROJECT]:agent_observability.multimodal_traces
```

### Step 3.5: Create the Log Sink (Traces to BigQuery)
To ensure all metric information (e.g., token usage) lands in BigQuery, we route the logs.
```bash
gcloud logging sinks create agent_logs_to_bq \
  bigquery.googleapis.com/projects/[YOUR_PROJECT]/datasets/agent_observability \
  --log-filter='severity>=INFO AND NOT logName:"cloudaudit.googleapis.com"' \
  --use-partitioned-tables
```

**Important:** After creating the Sink, Cloud Logging will inform you which special Service Account it created for the router. You must give that account edit permissions in BigQuery:
```bash
gcloud projects add-iam-policy-binding [YOUR_PROJECT] \
  --member="serviceAccount:service-[PROJECT_NUMBER]@gcp-sa-logging.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

### Step 3.6: Configure Cloud Monitoring for ADK Metrics (Histograms)
To export OpenTelemetry native metrics (like `gen_ai.invoke_agent.duration`, `gen_ai.client.token.usage`) to BigQuery, we first send them to Cloud Monitoring (already configured in `agent.py`). Then, we export them from Monitoring to BigQuery.

Currently, this requires configuring a Cloud Monitoring export or using federated queries in BigQuery:
1. Go to the [Metrics Explorer](https://console.cloud.google.com/monitoring/metrics-explorer) in GCP.
2. The ADK metrics will appear under the prefix `workload.googleapis.com/gen_ai`.
3. To query these from BigQuery, you can configure [Cloud Monitoring as an External Data Source](https://cloud.google.com/bigquery/docs/cloud-monitoring-federated-queries) in BigQuery, or set up a [Metrics Export](https://cloud.google.com/monitoring/export-metrics) if long-term storage of these specific aggregations is required.

---

## 4. Official Reference Links

If you need to dig deeper into how Google Cloud teams built this instrumentation and the advanced telemetry options:

1. **Multimodal Collection (The core of our solution)**: [Collect and view multimodal prompts and responses](https://docs.cloud.google.com/stackdriver/docs/instrumentation/collect-view-multimodal-prompts-responses)
2. **ADK with OpenTelemetry**: [Instrument ADK applications with OpenTelemetry](https://docs.cloud.google.com/stackdriver/docs/instrumentation/ai-agent-adk)
3. **OpenTelemetry Semantics for GenAI**: [Semantic Conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
4. **Log Routing to BigQuery**: [Route logs to supported destinations](https://cloud.google.com/logging/docs/export/configure_export_v2)
