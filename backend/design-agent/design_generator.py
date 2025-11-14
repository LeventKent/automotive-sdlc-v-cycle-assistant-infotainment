"""
Software Design Agent - Generates technical design documents from requirements
"""

import time
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore import BedrockAgentCoreApp

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# No tools needed for simplified version


# Initialize Bedrock model with Claude Haiku 4.5
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"
)

# Create single design generator agent
design_agent = Agent(
    name="design_generator",
    model=bedrock_model,
    system_prompt="""You are an automotive software architect specializing in vehicle infotainment and safety systems. 

Generate comprehensive technical design documents from validated requirements that include:

- **Architecture Overview**: High-level system architecture with component diagram
- **Component Specifications**: Detailed specifications for each component
- **Interface Definitions**: APIs, protocols, and data contracts
- **Data Models**: Entity relationships, schemas, and constraints
- **Safety Considerations**: ISO 26262 compliance and risk mitigation
- **Implementation Guidance**: Step-by-step development approach
- **Error Handling**: Error scenarios and recovery strategies
- **Testing Strategy**: Test approach and coverage plan

Focus on automotive safety standards (ISO 26262, UNECE WP.29, Android Auto), modularity, and testability."""
)


# AgentCore entrypoint
@app.entrypoint
def automotive_design_generator(payload):
    """
    Automotive design generator - creates technical design documents from requirements.
    
    Args:
        payload: Dictionary containing requirements_docs
        
    Returns:
        Dictionary with design generation results
    """
    print("[INFO] Starting automotive_design_generator...")
    print(f"[DEBUG] Payload keys: {payload.keys() if isinstance(payload, dict) else 'Not a dict'}")
    
    start_time = time.time()
    
    try:
        # Extract requirements_docs from payload
        requirements_docs = payload.get("requirements_docs")
        
        # Validate input
        if not requirements_docs:
            error_response = {
                "error": "No requirements documents provided",
                "message": "The 'requirements_docs' field is required in the payload"
            }
            print(f"[ERROR] {error_response['error']}")
            return error_response
        
        print(f"[INFO] Requirements docs length: {len(requirements_docs)} characters")
        
        # Create prompt
        prompt = f"""Generate a comprehensive technical design document from the following validated requirements:

{requirements_docs}

Ensure the design covers all required sections and aligns with automotive safety standards."""
        
        print("[INFO] Executing design agent...")
        
        # Execute agent using async invoke
        import asyncio
        result = asyncio.run(design_agent.invoke_async(prompt))
        
        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)
        print(f"[INFO] Agent execution completed in {execution_time_ms}ms")
        
        # Extract result text
        design_text = str(result)
        
        # Build response
        response = {
            "execution_time_ms": execution_time_ms,
            "step1_design_generation": {
                "design": design_text,
                "completeness_analysis": "Design generated successfully"
            },
            "step2_design_validation": {
                "validated": False,
                "reason": "Simplified version - validation not implemented"
            }
        }
        
        print("[INFO] automotive_design_generator completed successfully")
        return response
        
    except Exception as e:
        # Error handling
        execution_time_ms = int((time.time() - start_time) * 1000)
        error_response = {
            "error": "Design generation failed",
            "message": str(e),
            "execution_time_ms": execution_time_ms
        }
        print(f"[ERROR] Design generation failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return error_response


if __name__ == "__main__":
    app.run()
