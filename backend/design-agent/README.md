# Automotive Software Design Agent

This folder contains the backend implementation of the automotive software design agent system that bridges the gap between requirements analysis and code implementation.

## Overview

The Software Design Agent transforms validated requirements documents into comprehensive technical design documents for automotive software development. It uses a single-agent architecture powered by Anthropic Claude Haiku 4.5.

## Architecture

```
┌─────────────────────────────────────────────┐
│         Design Generator Agent              │
│  - Generates technical design documents     │
│  - Includes architecture, components,       │
│    interfaces, data models, safety          │
│  - Aligns with automotive standards         │
└─────────────────────────────────────────────┘
```

- **Agent**: Single design generator agent
- **Framework**: Strands Agents (simplified, no GraphBuilder)
- **Authentication**: Amazon Cognito with JWT tokens
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Model**: Anthropic Claude Haiku 4.5 (`us.anthropic.claude-haiku-4-5-20251001-v1:0`)

## Files

- `design_generator.py` - Main design generator agent implementation
- `utils.py` - Utility functions for Cognito authentication and user pool management
- `requirements.txt` - Python dependencies for the backend system
- `Dockerfile` - Container definition for AgentCore deployment (auto-generated during deployment)
- `deploy.sh` - Deployment script for AgentCore Runtime
- `check_runtime_logs.py` - Script to check CloudWatch logs for debugging
- `.bedrock_agentcore.yaml` - Agent configuration file (generated after first deployment)

## Key Features

### 1. Design Generation
- Generates comprehensive technical design documents from validated requirements
- Includes architecture diagrams, component specifications, interface definitions, and data models
- Aligns designs with automotive safety standards (ISO 26262, UNECE WP.29, Android Auto)
- References specific requirements for traceability
- Provides implementation guidance and testing strategies

### 2. AgentCore Runtime Deployment
- Deploys to Amazon Bedrock AgentCore Runtime
- Integrated with Amazon Cognito for secure access
- Docker-based containerization using `uv` package manager
- Structured response with execution metrics

### 3. IDE Integration
- Model Context Protocol (MCP) server for IDE integration
- Direct invocation from Kiro and other supported IDEs
- Seamless workflow integration with Requirements Analyzer and Code Analyzer
- Automatic configuration loading from `.bedrock_agentcore.yaml`

## Usage

### Deploying the Agent

1. Navigate to the backend/design-agent directory:
   ```bash
   cd automotive-strands-agents-in-runtime/backend/design-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Deploy to AgentCore Runtime:
   ```bash
   ./deploy.sh
   ```
   
   The deployment script will:
   - Check prerequisites (AWS credentials, Docker, Python packages)
   - Set up Cognito user pool (if needed)
   - Build and deploy Docker container to AgentCore
   - Test the deployed agent

4. Copy MCP configuration for design-agent (if not done already):
   ```bash
   cp ../../ide-support/kiro/settings/mcp.json ../../.kiro/settings/mcp.json
   ```

5. Restart Kiro to load the MCP server configuration

6. Test the agent using the MCP tool in Kiro:
   ```
   Use the automotive_design_generator tool with requirements documents
   ```

### Project Structure

The design agent is configured to work from the backend/design-agent directory with the following path structure:

```
automotive-strands-agents-in-runtime/
├── backend/                                    # Backend Services
│   ├── design-agent/                          # Design Generator Backend (current directory)
│   │   ├── design_generator.py                # Main agent implementation
│   │   ├── utils.py                           # Cognito utilities
│   │   ├── requirements.txt                   # Python dependencies
│   │   ├── deploy.sh                          # Deployment script
│   │   ├── check_runtime_logs.py              # Log checking utility
│   │   ├── Dockerfile                         # Auto-generated during deployment
│   │   └── .bedrock_agentcore.yaml            # Agent config (after deployment)
│   ├── requirements-agent/                    # Requirements Analyzer Backend
│   └── c-code-analyzer-agent/                 # C Code Analyzer Backend
├── mcp-servers/                               # MCP Server Implementations
│   ├── automotive-design-mcp/                 # Design Agent MCP Server
│   ├── automotive-requirements-mcp/           # Requirements Agent MCP Server
│   └── automotive-coding-mcp/                 # Coding Agent MCP Server
├── weather-app/                               # Sample Application
│   ├── business-requirements/                 # Business requirements documents
│   └── technical-requirements/                # Technical requirements documents
└── ide-support/                               # IDE Configuration
    └── kiro/
        ├── settings/mcp.json                  # MCP server configuration
        └── steering/design-agent-mcp-tool-use.md
```

## Dependencies

- `strands-agents==1.16.0` - Agent framework (note: imports as `strands`)
- `boto3>=1.34.0` - AWS SDK for Python
- `bedrock-agentcore>=0.1.0` - Amazon Bedrock AgentCore SDK
- `jupyter>=1.0.0` - Notebook environment
- `pyyaml>=6.0` - YAML configuration parsing

Install all dependencies:
```bash
pip install -r requirements.txt
```

**Important**: The package is installed as `strands-agents` but imported as `strands`:
```python
from strands import Agent
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder  # Not used in simplified version
```

## Workflow Integration

The Design Agent fits into the automotive software development workflow:

1. **Requirements Analyzer** → Validates business and technical requirements
2. **Design Agent** (this component) → Generates technical design documents
3. **Code Analyzer** → Validates C code implementation

### Input
- Validated requirements documents from the Requirements Analyzer
- Can use sample requirements from `weather-app/technical-requirements/`
- Plain text or markdown format

### Output
- Comprehensive technical design document with:
  - Architecture Overview
  - Component Specifications
  - Interface Definitions
  - Data Models
  - Safety Considerations
  - Implementation Guidance
  - Error Handling Strategies
  - Testing Strategy
- Execution time metrics
- Structured JSON response

## Sample Test Cases

The agent can process requirements from `weather-app/technical-requirements/`:

1. **Complete Requirements** (`weather_app_srs.md`): Well-structured requirements that generate comprehensive designs
2. **Partial Requirements**: Requirements with missing sections (agent will still generate best-effort design)

## Design Output Sections

The agent generates designs covering:

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

### Common Issues

1. **Deployment Failures**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check AWS credentials are configured: `aws configure`
   - Verify Docker is running for AgentCore deployment: `docker ps`
   - Review deployment script output for specific error messages

2. **Authentication Errors**
   - Verify Cognito user pool ID and client ID are correct in `.bedrock_agentcore.yaml`
   - Check JWT token is valid and not expired
   - Ensure IAM permissions are configured for Bedrock access

3. **Import Errors**
   - **ModuleNotFoundError: No module named 'strands_agents'**: The package is `strands-agents` but imports as `strands`
   - Correct import: `from strands import Agent`
   - Incorrect import: `from strands_agents import Agent`

4. **Design Generation Issues**
   - Verify requirements document format is correct (plain text or markdown)
   - Check that requirements are reasonably complete
   - Ensure model ID is correct: `us.anthropic.claude-haiku-4-5-20251001-v1:0`
   - Review CloudWatch logs for runtime errors

5. **MCP Server Connection Issues**
   - Verify MCP configuration in `.kiro/settings/mcp.json`
   - Ensure `.bedrock_agentcore.yaml` path is correct in `design-server.py`
   - Restart Kiro to reload MCP server configuration
   - Check MCP server logs for connection errors

6. **424 "Failed Dependency" Errors**
   - Runtime failed to start - check CloudWatch logs
   - Missing dependencies in Docker container
   - Import errors in `design_generator.py`
   - Use `check_runtime_logs.py` to view detailed error messages:
     ```bash
     python check_runtime_logs.py <runtime-id>-DEFAULT
     ```

### Debug Tips

- Check CloudWatch logs: `/aws/bedrock-agentcore/runtimes/<runtime-id>-DEFAULT`
- Use `check_runtime_logs.py` script to view runtime logs
- Test Docker build locally: `docker build -t test-design-agent .`
- Verify imports in container: `docker run --rm test-design-agent python -c "import strands; print('OK')"`
- Review deployment output for agent ARN and runtime ID

## Security

- Inbound authentication using Amazon Cognito
- JWT token validation for all requests
- IAM role-based permissions for Bedrock access
- Secure deployment on AgentCore Runtime
- Input sanitization to prevent injection attacks

## Cleanup

To remove deployed resources:

1. **Via AWS Console**:
   - Navigate to Bedrock AgentCore Runtime
   - Delete the runtime instance
   - Clean up ECR repositories if needed
   - Remove IAM roles (if auto-created)

2. **Via CLI** (if available):
   ```bash
   # Delete runtime (requires AWS CLI with AgentCore support)
   aws bedrock-agentcore delete-runtime --runtime-id <runtime-id>
   ```

Note: Manual cleanup of IAM roles and ECR repositories may be required.

## Related Agents

This agent is part of a three-agent automotive software development workflow:

1. **[Requirements Analyzer](../requirements-agent/README.md)**: Validates business and technical requirements, generates user acceptance tests
2. **Design Agent** (this component): Generates technical design documents from validated requirements
3. **[C Code Analyzer](../c-code-analyzer-agent/README.md)**: Validates C code implementation, generates unit tests

## Next Steps

- Integrate design generation with code scaffolding
- Add support for visual design tools (interactive diagrams)
- Implement design versioning and change tracking
- Extend automotive standards coverage (ISO 26262, ASPICE)
- Add collaborative design review workflows
- Create design templates for common automotive patterns
