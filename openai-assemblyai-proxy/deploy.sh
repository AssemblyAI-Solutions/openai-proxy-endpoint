#!/bin/bash

# OpenAI to AssemblyAI Proxy API Deployment Script
# This script deploys the service to Google Cloud Run

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="openai-assemblyai-proxy"
MEMORY="1Gi"
TIMEOUT="900"
MAX_INSTANCES="100"
CONCURRENCY="80"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying OpenAI to AssemblyAI Proxy API${NC}"
echo "=================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo "Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not logged in to gcloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if project is set
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$CURRENT_PROJECT" ]; then
    echo -e "${YELLOW}⚠️  No project set${NC}"
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Project: $CURRENT_PROJECT"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check for AssemblyAI API key
if [ -z "$ASSEMBLYAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ASSEMBLYAI_API_KEY environment variable not set${NC}"
    read -p "Enter your AssemblyAI API key: " ASSEMBLYAI_API_KEY
    if [ -z "$ASSEMBLYAI_API_KEY" ]; then
        echo -e "${RED}❌ AssemblyAI API key is required${NC}"
        exit 1
    fi
fi

# Enable required APIs
echo -e "${GREEN}📋 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Deploy to Cloud Run
echo -e "${GREEN}🔨 Building and deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --memory $MEMORY \
    --timeout $TIMEOUT \
    --set-env-vars "ASSEMBLYAI_API_KEY=$ASSEMBLYAI_API_KEY,PORT=8080,LOG_LEVEL=INFO,TIMEOUT_SECONDS=300" \
    --max-instances $MAX_INSTANCES \
    --concurrency $CONCURRENCY \
    --platform managed

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo "=================================="
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test the service:"
echo "curl $SERVICE_URL/health"
echo ""
echo "Example transcription request:"
echo "curl -X POST $SERVICE_URL/v1/audio/transcriptions \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"audio_url\": \"https://example.com/audio.wav\", \"model\": \"whisper-1\"}'"
echo ""
echo -e "${YELLOW}💡 Remember to set up monitoring and logging in the Cloud Console${NC}"
