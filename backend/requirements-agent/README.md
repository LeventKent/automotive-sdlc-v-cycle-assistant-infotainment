# Backend - Automotive Requirements Analyzer

This folder contains the backend implementation of the automotive requirements analyzer system.

## Files

- `automotive_requirements_agent_notebook.ipynb` - Main Jupyter notebook demonstrating the multi-agent system
- `requirements_analyzer.py` - Full Strands-based requirements analyzer implementation
- `utils.py` - Utility functions for Cognito authentication and user pool management
- `requirements.txt` - Python dependencies for the backend system

## Usage

### Running the Notebook

1. Navigate to the backend directory:
   ```bash
   cd automotive-strands-agents-in-runtime/backend
   ```

2. Run steps in the Jupyter Notebook:
   ```bash
   jupyter notebook automotive_requirements_agent_notebook.ipynb
   ```
   Execute the notebook cells (automatically installs dependencies from requirements.txt)

3. Copy MCP configuration for requirements-agent (if not done already):
   ```bash
   cp ide-support/kiro/settings/mcp.json .kiro/settings/mcp.json
   ```
4. Validate in Kiro that the MCP server automotive-requirements is running correctly.

### Path Configuration

The notebook and analyzer are configured to work from the backend directory with the following path structure:

```
automotive-strands-agents-in-runtime/
├── backend/                                    # Backend Services
│   └── requirements-agent/                    # Requirements Analyzer Backend (current directory)
│       ├── automotive_requirements_agent_notebook.ipynb
│       ├── requirements_analyzer.py
│       ├── utils.py
│       └── requirements.txt
├── requirements/weather-app/business/          # Business requirements documents
│   └── weather_app_brd.md
└── requirements/weather-app/technical/         # Technical requirements documents
    └── weather_app_srs.md
```

### Key Features

1. **Business Requirements Focus**: Analyzes documents from `../weather-app/business-requirements/`
2. **Multi-Agent Architecture**: Uses Strands agents with conditional execution
3. **AgentCore Runtime**: Deploys to Amazon Bedrock AgentCore Runtime
4. **Authentication**: Integrated with Amazon Cognito for secure access
5. **User Acceptance Tests**: Generates comprehensive test specifications

### Dependencies

- `strands-agents` - Multi-agent framework
- `boto3` - AWS SDK for Python
- `bedrock-agentcore` - Amazon Bedrock AgentCore SDK
- `jupyter` - Notebook environment

### Troubleshooting

If you encounter deployment issues:

1. Ensure all dependencies are installed
2. Check AWS credentials are configured
3. Verify Docker is running for AgentCore deployment
4. Review the notebook output for specific error messages

For 424 "Failed Dependency" errors, the issue is typically related to:
- Missing dependencies in requirements.txt
- Docker container build failures
- Import errors in the Python code