#!/bin/bash

################################################################################
# Automotive Design Agent Deployment Script
# 
# This script deploys the Software Design Agent to Amazon Bedrock AgentCore Runtime
# with inbound authentication using Amazon Cognito.
#
# Prerequisites:
# - AWS credentials configured
# - Docker running
# - Python 3.13+ with required packages
# - AWS CLI installed
#
# Usage:
#   ./deploy.sh [options]
#
# Options:
#   --agent-name NAME       Custom agent name (default: automotive_design_generator)
#   --region REGION         AWS region (default: us-west-2)
#   --skip-cognito          Skip Cognito setup (use existing)
#   --cleanup               Clean up existing deployment
#   --help                  Show this help message
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AGENT_NAME="automotive_design_generator"
REGION="us-west-2"
SKIP_COGNITO=false
CLEANUP=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent-name)
            AGENT_NAME="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --skip-cognito)
            SKIP_COGNITO=true
            shift
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --help)
            head -n 30 "$0" | tail -n 25
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check Docker
    #if ! docker info &> /dev/null; then
    #    log_error "Docker is not running. Please start Docker."
    #    exit 1
    #fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed."
        exit 1
    fi
    
    # Check required Python packages
    if ! python3 -c "import strands" &> /dev/null; then
        log_error "strands-agents package not installed. Run: pip install -r requirements.txt"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Setup Cognito User Pool
setup_cognito() {
    if [ "$SKIP_COGNITO" = true ]; then
        log_info "Skipping Cognito setup (--skip-cognito flag set)"
        return
    fi
    
    log_info "Setting up Amazon Cognito User Pool..."
    
    python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from utils import setup_cognito_user_pool

config = setup_cognito_user_pool()
if config:
    print(f"COGNITO_CLIENT_ID={config['client_id']}")
    print(f"COGNITO_DISCOVERY_URL={config['discovery_url']}")
    print(f"COGNITO_POOL_ID={config['pool_id']}")
else:
    print("ERROR: Failed to setup Cognito")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Cognito User Pool configured"
    else
        log_error "Failed to setup Cognito User Pool"
        exit 1
    fi
}

# Deploy agent to AgentCore Runtime
deploy_agent() {
    log_info "Deploying ${AGENT_NAME} to AgentCore Runtime..."
    
    python3 << EOF
import sys
import time
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
from utils import setup_cognito_user_pool

# Get Cognito configuration
cognito_config = setup_cognito_user_pool()
if not cognito_config:
    print("ERROR: Failed to get Cognito configuration")
    sys.exit(1)

discovery_url = cognito_config['discovery_url']
client_id = cognito_config['client_id']

# Initialize runtime
boto_session = Session()
region = boto_session.region_name

agentcore_runtime = Runtime()

# Configure
print(f"Configuring agent: ${AGENT_NAME}")
response = agentcore_runtime.configure(
    entrypoint="design_generator.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name="${AGENT_NAME}",
    authorizer_configuration={
        "customJWTAuthorizer": {
            "discoveryUrl": discovery_url,
            "allowedClients": [client_id]
        }
    }
)
print(f"Configuration response: {response}")

# Launch
print(f"Launching agent to AgentCore Runtime...")
launch_result = agentcore_runtime.launch()
print(f"Launch result: {launch_result}")

# Wait for deployment
print("Waiting for deployment to complete...")
status_response = agentcore_runtime.status()
status = status_response.endpoint['status']
end_status = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']

print(f"Initial status: {status}")
while status not in end_status:
    time.sleep(10)
    status_response = agentcore_runtime.status()
    status = status_response.endpoint['status']
    print(f"Status: {status}")

if status == 'READY':
    print(f"DEPLOYMENT_SUCCESS")
    print(f"AGENT_ID={launch_result.agent_id}")
    print(f"AGENT_ARN={launch_result.agent_arn}")
    print(f"ECR_URI={launch_result.ecr_uri}")
else:
    print(f"ERROR: Deployment failed with status: {status}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Agent deployed successfully"
    else
        log_error "Agent deployment failed"
        exit 1
    fi
}

# Test the deployed agent
test_agent() {
    log_info "Testing deployed agent..."
    
    python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from bedrock_agentcore_starter_toolkit import Runtime
from utils import reauthenticate_user, setup_cognito_user_pool

# Get Cognito configuration
cognito_config = setup_cognito_user_pool()
if not cognito_config:
    print("ERROR: Failed to get Cognito configuration")
    sys.exit(1)

# Get bearer token
bearer_token = reauthenticate_user(cognito_config['client_id'])

# Initialize runtime
agentcore_runtime = Runtime()

# Test with minimal requirements
test_requirements = """
# Test Requirements Document

## System Overview
A simple automotive weather application.

## Functional Requirements
- FR-001: Display current temperature
- FR-002: Show weather icons
- FR-003: Voice command support

## Non-Functional Requirements
- NFR-001: Load within 3 seconds
- NFR-002: Use TLS 1.2+
"""

print("Invoking agent with test requirements...")
try:
    response = agentcore_runtime.invoke(
        {"requirements_docs": test_requirements},
        bearer_token=bearer_token
    )
    print("TEST_SUCCESS")
    print(f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
except Exception as e:
    print(f"TEST_FAILED: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Agent test passed"
    else
        log_warning "Agent test failed (agent may still be initializing)"
    fi
}

# Cleanup existing deployment
cleanup_deployment() {
    log_info "Cleaning up existing deployment..."
    
    python3 << EOF
import sys
import boto3
from boto3.session import Session

boto_session = Session()
region = boto_session.region_name

# List and delete agent runtimes
try:
    agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
    
    # Note: This requires the agent ID which we don't have here
    # Users should manually clean up via AWS Console or provide agent ID
    print("Please manually clean up agent runtimes via AWS Console")
    print("Or use the notebook cleanup cells")
    
except Exception as e:
    print(f"Cleanup note: {e}")
EOF
    
    log_info "Cleanup instructions provided"
}

# Main execution
main() {
    echo "=================================="
    echo "Automotive Design Agent Deployment"
    echo "=================================="
    echo ""
    echo "Agent Name: ${AGENT_NAME}"
    echo "Region: ${REGION}"
    echo ""
    
    if [ "$CLEANUP" = true ]; then
        cleanup_deployment
        exit 0
    fi
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run deployment steps
    check_prerequisites
    setup_cognito
    deploy_agent
    test_agent
    
    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Check CloudWatch logs for runtime status"
    echo "2. Test the agent using the notebook or MCP server"
    echo "3. Configure Kiro IDE with the Cognito client ID"
    echo ""
}

# Run main function
main
