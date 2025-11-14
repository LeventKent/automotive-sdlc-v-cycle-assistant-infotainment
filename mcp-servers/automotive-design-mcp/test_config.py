#!/usr/bin/env python3
"""
Test configuration and sample usage for Automotive Design MCP Server
"""

import json
import os
from design_server import agent

# Sample requirements document for testing
SAMPLE_REQUIREMENTS = """
# Weather Application Requirements

## Introduction

The Weather Application is an automotive infotainment system component that provides real-time weather information and forecasts to drivers through Android Auto integration.

## Glossary

- **Weather Application**: The automotive infotainment system component for weather information
- **Android Auto**: Google's platform for integrating mobile apps with vehicle infotainment systems
- **Voice Command System**: Google Assistant integration for hands-free operation
- **Weather API**: External service providing weather data

## Requirements

### Requirement 1

**User Story:** As a driver, I want to view current weather conditions, so that I can make informed decisions about my journey

#### Acceptance Criteria

1. WHEN the application launches, THE Weather Application SHALL display current temperature within 2 seconds
2. THE Weather Application SHALL display current weather conditions including humidity, wind speed, and precipitation
3. THE Weather Application SHALL update weather data every 15 minutes automatically
4. IF network connection fails, THEN THE Weather Application SHALL display cached weather data with timestamp
5. THE Weather Application SHALL display weather icon matching current conditions

### Requirement 2

**User Story:** As a driver, I want to see a 7-day weather forecast, so that I can plan future trips

#### Acceptance Criteria

1. THE Weather Application SHALL display a 7-day weather forecast with daily high and low temperatures
2. WHEN the user selects a forecast day, THE Weather Application SHALL display detailed hourly forecast
3. THE Weather Application SHALL display precipitation probability for each forecast day
4. THE Weather Application SHALL update forecast data every 60 minutes
5. WHERE forecast data is unavailable, THE Weather Application SHALL display "Data Unavailable" message

### Requirement 3

**User Story:** As a driver, I want to use voice commands to check weather, so that I can keep my eyes on the road

#### Acceptance Criteria

1. THE Weather Application SHALL support Google Assistant voice commands for weather queries
2. WHEN the user says "What's the weather", THE Weather Application SHALL respond with current conditions via voice
3. THE Weather Application SHALL support voice queries for specific locations
4. THE Weather Application SHALL provide voice responses within 3 seconds of command
5. IF voice recognition fails, THEN THE Weather Application SHALL prompt user to repeat command

### Requirement 4

**User Story:** As a driver, I want the app to comply with Android Auto guidelines, so that it is safe to use while driving

#### Acceptance Criteria

1. THE Weather Application SHALL comply with Android Auto driver distraction guidelines
2. THE Weather Application SHALL limit text display to essential information only
3. THE Weather Application SHALL use large touch targets (minimum 48dp) for all interactive elements
4. WHILE the vehicle is in motion, THE Weather Application SHALL disable manual text entry
5. THE Weather Application SHALL support night mode with reduced brightness

### Requirement 5

**User Story:** As a driver, I want to receive severe weather alerts, so that I can take appropriate safety measures

#### Acceptance Criteria

1. WHEN severe weather alerts are issued, THE Weather Application SHALL display alert notification immediately
2. THE Weather Application SHALL prioritize severe weather alerts over other displays
3. THE Weather Application SHALL provide voice notification for severe weather alerts
4. THE Weather Application SHALL display alert details including affected areas and duration
5. THE Weather Application SHALL allow user to dismiss alerts after acknowledgment
"""

# Sample incomplete requirements for testing
INCOMPLETE_REQUIREMENTS = """
# Simple Weather App

## Overview
A weather app for cars that shows weather information.

## Features
- Display current weather
- Show forecast
- Voice commands maybe
- Android Auto support

## Technical Notes
- Should be fast
- Must work offline sometimes
- Need to handle errors
"""

def test_design_generation():
    """Test the design generation functionality with complete requirements"""
    print("Testing Automotive Design Generation with Complete Requirements...")
    print("=" * 60)
    
    try:
        # Test with sample requirements
        result = agent.invoke_agent(SAMPLE_REQUIREMENTS)
        
        print("Design generation completed successfully!")
        print("\nResults Summary:")
        print(f"Execution Time: {result.get('execution_time_ms', 'N/A')} ms")
        
        # Display design generation results
        step1 = result.get('step1_design_generation', {})
        if step1:
            print("\n--- Step 1: Design Generation ---")
            completeness = step1.get('completeness_analysis', 'N/A')
            print(f"Completeness Analysis: {completeness[:200]}..." if len(str(completeness)) > 200 else f"Completeness Analysis: {completeness}")
            
            design = step1.get('design', '')
            print(f"\nDesign Document Length: {len(design)} characters")
            print(f"Design Preview: {design[:300]}..." if len(design) > 300 else f"Design: {design}")
        
        # Display validation results
        step2 = result.get('step2_design_validation', {})
        if step2:
            print("\n--- Step 2: Design Validation ---")
            validated = step2.get('validated', False)
            print(f"Validated: {validated}")
            
            if validated:
                validation_report = step2.get('validation_report', 'N/A')
                quality_score = step2.get('quality_score', 'N/A')
                print(f"Quality Score: {quality_score}")
                print(f"Validation Report Preview: {str(validation_report)[:200]}...")
            else:
                reason = step2.get('reason', 'Unknown')
                print(f"Validation Skipped - Reason: {reason}")
        
        print("\n" + "=" * 60)
        return result
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_incomplete_requirements():
    """Test with incomplete requirements to verify completeness analysis"""
    print("\nTesting with Incomplete Requirements...")
    print("=" * 60)
    
    try:
        result = agent.invoke_agent(INCOMPLETE_REQUIREMENTS)
        
        print("Analysis of incomplete requirements completed!")
        print("\nResults Summary:")
        print(f"Execution Time: {result.get('execution_time_ms', 'N/A')} ms")
        
        # Display design generation results
        step1 = result.get('step1_design_generation', {})
        if step1:
            print("\n--- Step 1: Design Generation ---")
            completeness = step1.get('completeness_analysis', 'N/A')
            print(f"Completeness Analysis: {completeness}")
            
            # Check if HIGH severity issues were detected
            if 'HIGH' in str(completeness).upper():
                print("\n✓ HIGH severity issues detected as expected for incomplete requirements")
        
        # Check if validation was skipped
        step2 = result.get('step2_design_validation', {})
        if step2:
            validated = step2.get('validated', False)
            if not validated:
                print("\n✓ Design validation was correctly skipped due to completeness issues")
                print(f"Reason: {step2.get('reason', 'Unknown')}")
        
        print("\n" + "=" * 60)
        return result
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_authentication():
    """Test Cognito authentication configuration"""
    print("\nTesting Authentication Configuration...")
    print("=" * 60)
    
    # Check environment variables
    required_env_vars = ["COGNITO_CLIENT_ID", "COGNITO_USERNAME", "COGNITO_PASSWORD"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠ Warning: Missing environment variables: {missing_vars}")
        print("\nTo enable automatic authentication, set these variables:")
        for var in missing_vars:
            print(f"  export {var}='your_value'")
        print("\nWithout these variables, you'll need to provide a bearer token manually.")
        return False
    else:
        print("✓ All required environment variables are set")
        
        # Test token generation
        try:
            token = agent.get_bearer_token()
            if token:
                print("✓ Successfully generated bearer token")
                print(f"  Token length: {len(token)} characters")
                print(f"  Token preview: {token[:20]}...")
                return True
            else:
                print("✗ Failed to generate bearer token")
                return False
        except Exception as e:
            print(f"✗ Authentication test failed: {str(e)}")
            return False

def validate_agent_config():
    """Validate agent configuration"""
    print("\nValidating Agent Configuration...")
    print("=" * 60)
    
    from design_server import AGENT_CONFIG
    
    required_fields = ["agent_id", "agent_arn", "agent_session_id", "region"]
    
    print("Agent Configuration:")
    for field in required_fields:
        value = AGENT_CONFIG.get(field, 'MISSING')
        status = "✓" if value and value != 'MISSING' else "✗"
        # Mask sensitive values
        display_value = value[:30] + "..." if len(str(value)) > 30 else value
        print(f"  {status} {field}: {display_value}")
    
    # Check authorizer configuration
    auth_config = AGENT_CONFIG.get('authorizer_configuration')
    if auth_config:
        print("  ✓ authorizer_configuration: Present")
        if 'customJWTAuthorizer' in auth_config:
            print("    ✓ customJWTAuthorizer: Configured")
    else:
        print("  ✗ authorizer_configuration: Missing")
    
    print("=" * 60)

if __name__ == "__main__":
    print("Automotive Design MCP Server - Test Configuration")
    print("=" * 60)
    print()
    
    # Validate configuration
    validate_agent_config()
    print()
    
    # Test authentication
    auth_ok = test_authentication()
    print()
    
    if not auth_ok:
        print("⚠ Authentication not configured. Tests will be skipped.")
        print("Please configure Cognito credentials to run full tests.")
    else:
        # Run design generation tests
        print("Running Design Generation Tests...")
        print()
        
        # Test 1: Complete requirements
        result1 = test_design_generation()
        
        # Test 2: Incomplete requirements
        result2 = test_incomplete_requirements()
        
        print("\n" + "=" * 60)
        print("Test Configuration Completed!")
        print("=" * 60)
        
        # Summary
        print("\nTest Summary:")
        print(f"  Complete Requirements Test: {'✓ PASSED' if result1 else '✗ FAILED'}")
        print(f"  Incomplete Requirements Test: {'✓ PASSED' if result2 else '✗ FAILED'}")
