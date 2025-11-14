#!/usr/bin/env python3
"""
Test the deployed agent using direct AWS SDK calls
"""
import boto3
import json
from utils import reauthenticate_user, setup_cognito_user_pool

# Agent details from deployment
AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:009537862394:runtime/automotive_design_generator-iljQM66OrQ"
REGION = "us-west-2"

def test_agent():
    """Test the deployed agent"""
    
    # Get Cognito configuration
    print("Setting up authentication...")
    cognito_config = setup_cognito_user_pool()
    if not cognito_config:
        print("ERROR: Failed to get Cognito configuration")
        return False
    
    # Get bearer token
    print("Getting authentication token...")
    bearer_token = reauthenticate_user(cognito_config['client_id'])
    
    # Create Bedrock AgentCore client
    print("Creating Bedrock AgentCore client...")
    client = boto3.client('bedrock-agentcore-runtime', region_name=REGION)
    
    # Test requirements
    test_requirements = """
# Test Requirements Document

## System Overview
A simple automotive weather application that displays current weather conditions.

## Functional Requirements
- FR-001: Display current temperature in Celsius and Fahrenheit
- FR-002: Show weather condition icons (sunny, cloudy, rainy, etc.)
- FR-003: Support voice command "What's the weather?"
- FR-004: Update weather data every 5 minutes

## Non-Functional Requirements
- NFR-001: Application must load within 3 seconds
- NFR-002: Use TLS 1.2+ for all network communications
- NFR-003: Support screen sizes from 7" to 12"
"""
    
    print("\n" + "="*80)
    print("Testing agent with sample requirements...")
    print("="*80 + "\n")
    
    try:
        # Invoke the agent
        response = client.invoke_agent(
            agentArn=AGENT_ARN,
            inputText=json.dumps({"requirements_docs": test_requirements}),
            authToken=bearer_token
        )
        
        print("\n" + "="*80)
        print("✅ Agent invocation successful!")
        print("="*80 + "\n")
        
        # Read the response stream
        print("Reading response...")
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    full_response += chunk['bytes'].decode('utf-8')
        
        print(f"\nResponse length: {len(full_response)} characters")
        
        # Try to parse as JSON
        try:
            response_data = json.loads(full_response)
            print("\nResponse keys:", list(response_data.keys()))
            
            if 'design_document' in response_data:
                print("\n--- Design Document Preview ---")
                design_doc = response_data['design_document']
                preview = design_doc[:500] if len(design_doc) > 500 else design_doc
                print(preview)
                if len(design_doc) > 500:
                    print(f"\n... (showing first 500 of {len(design_doc)} characters)")
        except json.JSONDecodeError:
            print("\nResponse (first 500 chars):")
            print(full_response[:500])
        
        return True
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ Agent invocation failed!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_agent()
    sys.exit(0 if success else 1)
