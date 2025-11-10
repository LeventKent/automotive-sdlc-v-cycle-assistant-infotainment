# Automotive Requirements MCP Server

This MCP server provides automotive requirements analysis capabilities using AWS Bedrock AgentCore Runtime.

## Features

- **Requirements Consistency Analysis**: Analyzes automotive requirements documents (BRDs, PRDs) for consistency, completeness, and quality
- **User Acceptance Test Generation**: Always generates comprehensive user acceptance tests regardless of analysis results
- **Automotive Standards Compliance**: Evaluates against automotive industry standards (ISO 26262, UNECE WP.29, Android Auto guidelines)
- **Multi-Agent Graph Architecture**: Uses Strands agents with sequential execution pattern

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables for Cognito authentication:
```bash
export COGNITO_CLIENT_ID="your_client_id"
export COGNITO_USERNAME="your_username" 
export COGNITO_PASSWORD="your_password"
```

## Usage

The server provides one main tool:

### `automotive_requirements_analyzer`

Analyzes automotive requirements documents and generates user acceptance tests.

**Parameters:**
- `requirements_docs` (str): The requirements documents content to analyze

**Returns:**
- JSON string containing analysis results and generated user acceptance tests

## Configuration

The server automatically loads agent configuration from `.bedrock_agentcore.yaml` file or uses fallback configuration for the automotive requirements analyzer agent.

## Authentication

Authentication is handled automatically using AWS Cognito credentials from environment variables. The server will obtain and refresh bearer tokens as needed.

## Agent Architecture

The underlying agent uses a sequential multi-agent graph:

1. **Requirements Consistency Analyzer**: Analyzes documents for consistency and quality
2. **User Acceptance Test Generator**: Always generates comprehensive test specifications

Both agents always execute, providing complete analysis and test coverage for all requirements.