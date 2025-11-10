#!/usr/bin/env python3
"""
Test configuration and sample usage for Automotive Requirements MCP Server
"""

import json
import os
from requirements_server import agent

# Sample requirements document for testing
SAMPLE_REQUIREMENTS = """
# Weather Application Requirements

## Business Requirements Document

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-100 | The application shall display current weather conditions | Must Have |
| FR-110 | The application shall display 7-day weather forecast | Must Have |
| FR-120 | The application shall support voice commands via Google Assistant | Should Have |

### Non-Functional Requirements

| ID | Requirement | Target Metric |
|---|---|---|
| NFR-100 | The application shall load weather data within 2 seconds | 2 seconds |
| NFR-110 | The application shall be compatible with Android Auto | 100% compliance |
| NFR-120 | The application shall handle network failures gracefully | 99.9% uptime |

### Use Cases

#### Use Case 1: Display Current Weather
**Trigger:** User opens weather application
**Flow:** 
1. System retrieves current location
2. System fetches weather data from API
3. System displays current conditions

**Success Criteria:** Weather data displayed within 2 seconds

### Safety Requirements
- Application must comply with driver distraction guidelines
- Voice commands must not require visual confirmation while driving
- Critical weather alerts must override other displays
"""

def test_requirements_analysis():
    """Test the requirements analysis functionality"""
    print("Testing Automotive Requirements Analysis...")
    print("=" * 60)
    
    try:
        # Test with sample requirements
        result = agent.invoke_agent(SAMPLE_REQUIREMENTS)
        
        print("Analysis completed successfully!")
        print("\nResults:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return None

def test_incomplete_requirements():
    """Test with incomplete requirements"""
    incomplete_reqs = """
    # Incomplete Requirements
    
    ## Basic Description
    A weather app for cars.
    
    ## Some Features
    - Show weather
    - Maybe voice commands
    
    ## Missing
    - No detailed requirements
    - No acceptance criteria
    - No performance metrics
    """
    
    print("\nTesting with incomplete requirements...")
    print("=" * 60)
    
    try:
        result = agent.invoke_agent(incomplete_reqs)
        print("Analysis of incomplete requirements completed!")
        print("\nResults:")
        print(json.dumps(result, indent=2))
        return result
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("Automotive Requirements MCP Server - Test Configuration")
    print("=" * 60)
    
    # Check environment variables
    required_env_vars = ["COGNITO_CLIENT_ID", "COGNITO_USERNAME", "COGNITO_PASSWORD"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        print("Set these variables for automatic authentication:")
        for var in missing_vars:
            print(f"  export {var}='your_value'")
        print()
    
    # Run tests
    test_requirements_analysis()
    test_incomplete_requirements()
    
    print("\nTest configuration completed!")