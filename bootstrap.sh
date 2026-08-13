#!/bin/bash
# -----------------------------------------------------------------------------
# AgentPlatform Bootstrap Script
# -----------------------------------------------------------------------------
# This script enables all the required Google Cloud APIs for AgentPlatform
# to function properly with the full observability suite
# (OpenTelemetry, Cloud Trace, Cloud Logging, and BigQuery).
# -----------------------------------------------------------------------------

set -e

# Validate that a PROJECT_ID was passed as an argument
if [ -z "$1" ]; then
    echo "❌ Error: You must provide your GCP Project ID."
    echo "💡 Usage: ./bootstrap.sh [YOUR_PROJECT_ID]"
    exit 1
fi

PROJECT_ID=$1

echo "============================================================"
echo "🚀 Starting AgentPlatform APIs Bootstrap"
echo "🌐 Target Project: $PROJECT_ID"
echo "============================================================"

# Enable the required APIs
echo "⏳ Enabling APIs (this may take a couple of minutes)..."

gcloud services enable \
    aiplatform.googleapis.com \
    bigquery.googleapis.com \
    cloudtrace.googleapis.com \
    logging.googleapis.com \
    storage.googleapis.com \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo "✅ All APIs were enabled successfully."
else
    echo "❌ There was an error enabling the APIs. Please check your permissions."
    exit 1
fi

echo "============================================================"
echo "🎉 Bootstrap finished successfully."
echo "============================================================"
echo ""
echo "Recommended next steps:"
echo "1. Run 'gcloud auth application-default login' if you haven't already."
echo "2. Check OBSERVABILITY_SETUP.md to create your Buckets and BigQuery Sinks."
