#!/usr/bin/env python3
"""
Test script to verify YAML configuration loading
"""

import yaml
import os

def test_yaml_loading():
    yaml_path = "./automotive-strands-agents-in-runtime/.bedrock_agentcore.yaml"
    
    if not os.path.exists(yaml_path):
        print(f"YAML file not found at: {yaml_path}")
        return False
    
    try:
        with open(yaml_path, 'r') as file:
            yaml_config = yaml.safe_load(file)
        
        print("YAML loaded successfully!")
        print("Default agent:", yaml_config.get('default_agent'))
        
        default_agent_name = yaml_config.get('default_agent')
        if default_agent_name:
            agent_config = yaml_config.get('agents', {}).get(default_agent_name)
            if agent_config:
                bedrock_config = agent_config.get('bedrock_agentcore', {})
                print("Agent ID:", bedrock_config.get('agent_id'))
                print("Agent ARN:", bedrock_config.get('agent_arn'))
                return True
        
        return False
        
    except Exception as e:
        print(f"Error loading YAML: {e}")
        return False

if __name__ == "__main__":
    test_yaml_loading()