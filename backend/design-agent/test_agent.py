#!/usr/bin/env python3
"""
Test script for the deployed automotive design agent
"""
import sys
from bedrock_agentcore_starter_toolkit import Runtime
from utils import reauthenticate_user, setup_cognito_user_pool

def test_agent():
    """Test the deployed agent with sample requirements"""
    
    # Get Cognito configuration
    print("Setting up authentication...")
    cognito_config = setup_cognito_user_pool()
    if not cognito_config:
        print("ERROR: Failed to get Cognito configuration")
        return False
    
    # Get bearer token
    print("Getting authentication token...")
    bearer_token = reauthenticate_user(cognito_config['client_id'])
    
    # Initialize runtime and check status of deployed agent
    print("Initializing runtime...")
    agentcore_runtime = Runtime()
    
    # Check if agent is deployed and ready
    try:
        status = agentcore_runtime.status()
        print(f"Agent status: {status.endpoint.get('status', 'UNKNOWN')}")
    except Exception as e:
        print(f"Note: Could not get status: {e}")
    
    # Test with minimal requirements
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
        response = agentcore_runtime.invoke(
            {"requirements_docs": test_requirements},
            bearer_token=bearer_token
        )
        
        print("\n" + "="*80)
        print("✅ Agent invocation successful!")
        print("="*80 + "\n")
        
        # Display response
        if isinstance(response, dict):
            print("Response keys:", list(response.keys()))
            
            if 'design_document' in response:
                print("\n--- Design Document Preview ---")
                design_doc = response['design_document']
                # Show first 500 characters
                preview = design_doc[:500] if len(design_doc) > 500 else design_doc
                print(preview)
                if len(design_doc) > 500:
                    print(f"\n... (showing first 500 of {len(design_doc)} characters)")
            
            if 'architecture_diagram' in response:
                print("\n--- Architecture Diagram ---")
                print(f"Diagram length: {len(response['architecture_diagram'])} characters")
            
            if 'component_specifications' in response:
                print("\n--- Component Specifications ---")
                specs = response['component_specifications']
                if isinstance(specs, list):
                    print(f"Number of components: {len(specs)}")
                    for i, comp in enumerate(specs[:3], 1):  # Show first 3
                        if isinstance(comp, dict) and 'name' in comp:
                            print(f"  {i}. {comp['name']}")
        else:
            print("Response type:", type(response))
            print("Response:", str(response)[:500])
        
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
    success = test_agent()
    sys.exit(0 if success else 1)
