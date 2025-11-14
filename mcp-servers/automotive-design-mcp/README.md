# Automotive Design MCP Server

This MCP server provides automotive technical design generation capabilities using AWS Bedrock AgentCore Runtime. It transforms validated requirements documents into comprehensive technical design documents.

## Features

- **Technical Design Generation**: Creates comprehensive design documents from validated requirements including architecture, components, interfaces, and data models
- **Single-Agent Architecture**: Uses a simplified Strands agent implementation
- **Automotive Standards Alignment**: Ensures designs align with ISO 26262, UNECE WP.29, and Android Auto guidelines
- **Automatic Authentication**: Handles Cognito JWT token management automatically
- **Configuration Auto-Loading**: Reads agent configuration from `.bedrock_agentcore.yaml`

## Architecture

The server implements a single-agent design generator:

```
┌─────────────────────────────────────────────┐
│         Design Generator Agent              │
│  - Generates technical design documents     │
│  - Includes architecture, components,       │
│    interfaces, data models, safety          │
│  - Aligns with automotive standards         │
└─────────────────────────────────────────────┘
```

**Design Generator**: 
- Generates comprehensive technical design documents
- Includes all required sections (architecture, components, interfaces, data models, safety, implementation guidance, error handling, testing)
- Powered by Anthropic Claude Haiku 4.5

## Installation

1. Install dependencies:
```bash
cd mcp-servers/automotive-design-mcp
pip install -r requirements.txt
```

2. Set up environment variables for Cognito authentication:
```bash
export COGNITO_CLIENT_ID="your_client_id"
export COGNITO_USERNAME="your_username" 
export COGNITO_PASSWORD="your_password"
```

3. Ensure the AgentCore agent is deployed and the `.bedrock_agentcore.yaml` configuration file is accessible.

## Configuration

### Agent Configuration

The server automatically loads agent configuration from `.bedrock_agentcore.yaml` file. The configuration should include:

```yaml
default_agent: automotive_design_generator

agents:
  automotive_design_generator:
    bedrock_agentcore:
      agent_id: "automotive_design_generator_inbound_auth_xxx"
      agent_arn: "arn:aws:bedrock-agentcore:us-west-2:account-id:runtime/automotive_design_generator_inbound_auth_xxx"
      agent_session_id: "xxx"  # Must be 33+ characters
    
    aws:
      region: "us-west-2"
    
    authorizer_configuration:
      customJWTAuthorizer:
        discoveryUrl: "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_xxx/.well-known/openid-configuration"
        allowedClients: ["xxx"]
```

The server searches for this file in multiple locations:
- Current directory
- Parent directories
- Common project paths

If the file is not found, it uses a fallback configuration (which will need to be updated with actual values).

### Environment Variables

Required for automatic authentication:
- `COGNITO_CLIENT_ID`: Your Cognito app client ID
- `COGNITO_USERNAME`: Your Cognito username
- `COGNITO_PASSWORD`: Your Cognito password

Optional:
- `AWS_REGION`: AWS region (default: us-west-2)

## Usage

### Running the MCP Server

```bash
python design-server.py
```

The server will start and listen for MCP tool invocations.

### Available Tools

#### `automotive_design_generator`

Generates technical design documents from validated requirements with completeness analysis and conditional validation.

**Parameters:**
- `requirements_docs` (str): The validated requirements documents content

**Returns:**
- JSON string containing:
  - `execution_time_ms`: Total execution time in milliseconds
  - `step1_design_generation`: Design generation results
    - `design`: Complete technical design document
    - `completeness_analysis`: Status message
  - `step2_design_validation`: Design validation results
    - `validated`: Always false (validation not implemented in simplified version)
    - `reason`: Explanation that validation is not implemented

**Example Response:**
```json
{
  "execution_time_ms": 172486,
  "step1_design_generation": {
    "design": "# Comprehensive Technical Design Document\n\n## Architecture Overview\n...",
    "completeness_analysis": "Design generated successfully"
  },
  "step2_design_validation": {
    "validated": false,
    "reason": "Simplified version - validation not implemented"
  }
}
```

### Testing the Server

Run the test configuration script to validate setup and test functionality:

```bash
python test_config.py
```

This will:
1. Validate agent configuration
2. Test Cognito authentication
3. Run design generation with sample requirements
4. Display results and summaries

## Authentication

Authentication is handled automatically using AWS Cognito credentials from environment variables. The server:

1. Obtains JWT bearer tokens using Cognito USER_PASSWORD_AUTH flow
2. Caches tokens and refreshes them automatically (tokens expire after 1 hour)
3. Includes bearer tokens in all AgentCore API requests

If environment variables are not set, authentication will fail and tests will be skipped.

## IDE Integration

### Kiro Configuration

Add to `ide-support/kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "automotive-design": {
      "command": "python",
      "args": ["mcp-servers/automotive-design-mcp/design-server.py"],
      "env": {
        "COGNITO_CLIENT_ID": "${COGNITO_CLIENT_ID}",
        "COGNITO_USERNAME": "${COGNITO_USERNAME}",
        "COGNITO_PASSWORD": "${COGNITO_PASSWORD}",
        "AWS_REGION": "us-west-2"
      }
    }
  }
}
```

### Usage in Kiro

Once configured, you can use the tool in Kiro:

```
Use the mcp_automotive_design_automotive_design_generator tool to generate 
a technical design from these requirements: [paste requirements]
```

The tool will:
1. Generate a comprehensive technical design
2. Return structured results with design document and execution metrics

## Design Output Sections

The design generator creates comprehensive technical designs covering:

| Section | Description |
|---------|-------------|
| Architecture Overview | High-level system architecture with component diagrams |
| Component Specifications | Detailed specifications for each component |
| Interface Definitions | APIs, protocols, and data contracts |
| Data Models | Entity relationships, schemas, and constraints |
| Safety Considerations | ISO 26262 compliance and risk mitigation |
| Implementation Guidance | Step-by-step development approach |
| Error Handling | Error scenarios and recovery strategies |
| Testing Strategy | Test approach, coverage plan, and test types |

## Troubleshooting

### Authentication Errors

**Problem**: "Authentication failed" or "Failed to obtain bearer token"

**Solutions:**
1. Verify environment variables are set correctly:
   ```bash
   echo $COGNITO_CLIENT_ID
   echo $COGNITO_USERNAME
   # Don't echo password for security
   ```

2. Verify Cognito user pool and client configuration
3. Check that user has correct permissions
4. Ensure password is correct and account is not locked

### Configuration Errors

**Problem**: "Could not find .bedrock_agentcore.yaml file"

**Solutions:**
1. Ensure the YAML file exists in the backend/design-agent directory
2. Check file permissions
3. Verify YAML syntax is correct
4. Update fallback configuration in design-server.py if needed

### Agent Invocation Errors

**Problem**: "AgentCore API error (424)" or "Failed to invoke AgentCore agent"

**Solutions:**
1. Verify agent is deployed and running: `./deploy.sh` in backend/design-agent
2. Check agent ARN and ID are correct in `.bedrock_agentcore.yaml`
3. Verify network connectivity to AgentCore endpoint
4. Check CloudWatch logs for agent execution errors:
   ```bash
   python backend/design-agent/check_runtime_logs.py <runtime-id>-DEFAULT
   ```
5. Common issues:
   - Runtime failed to start (check logs for import errors)
   - Missing dependencies in Docker container
   - Incorrect agent configuration

### Import Errors in Runtime

**Problem**: "ModuleNotFoundError: No module named 'strands_agents'" in CloudWatch logs

**Solutions:**
1. The package is `strands-agents` but imports as `strands`
2. Verify imports in `design_generator.py`:
   ```python
   from strands import Agent  # Correct
   from strands_agents import Agent  # Incorrect
   ```
3. Redeploy after fixing imports: `./deploy.sh`

## Related Components

- **Requirements Analyzer Agent**: Upstream agent that validates requirements before design generation
- **Code Analyzer Agent**: Downstream agent that validates C code implementation against designs
- **Backend Design Agent**: The Strands agent implementation deployed on AgentCore Runtime (see `backend/design-agent/`)

## Development

### Project Structure

```
mcp-servers/automotive-design-mcp/
├── design-server.py          # MCP server implementation
├── requirements.txt          # Python dependencies
├── test_config.py           # Configuration testing and validation
└── README.md                # This file
```

### Running Tests

```bash
# Run configuration tests
python test_config.py

# Test with custom requirements
python -c "
from design_server import agent
result = agent.invoke_agent('your requirements here')
print(result)
"
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check CloudWatch logs for agent execution details:
```bash
# Use the check_runtime_logs.py script
python backend/design-agent/check_runtime_logs.py <runtime-id>-DEFAULT

# Or use AWS CLI directly
aws logs tail /aws/bedrock-agentcore/runtimes/<runtime-id>-DEFAULT --follow
```

Common log locations:
- Runtime logs: `/aws/bedrock-agentcore/runtimes/<runtime-id>-DEFAULT`
- Log stream prefix: `[runtime-logs]`

## Support

For issues or questions:
1. Check CloudWatch logs for detailed error messages
2. Verify all configuration steps are completed
3. Test authentication separately using test_config.py
4. Review the design agent implementation in backend/design-agent/

## License

This MCP server is part of the Automotive Strands Agents project.
