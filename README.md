# Automotive Multi-Agent Analysis System

This project implements multiple multi-agent systems for automotive software development using Strands agents deployed on Amazon Bedrock AgentCore Runtime with inbound authentication, plus Model Context Protocol (MCP) servers for IDE integration.

## Components

### 1. C Code Analyzer Agent
Multi-agent system for automotive C code analysis with custom automotive coding standards compliance checking and unit test generation.

**Key Features:**
- Analyzes C code for custom automotive coding standards violations (AUTO-SAFE-001, AUTO-MEM-001, AUTO-FUNC-001, AUTO-STYLE-001)
- Categorizes violations by severity (LOW, MEDIUM, HIGH)
- Conditionally generates comprehensive unit tests for compliant code
- Includes edge cases, boundary conditions, and automotive testing standards

**Location:** `backend/c-code-analyzer-agent/`  
**MCP Server:** `mcp-servers/automotive-coding-mcp/`  
**Documentation:** See [C Code Analyzer README](backend/c-code-analyzer-agent/README.md) for detailed setup and usage instructions.

### 2. Requirements Analyzer Agent  
Multi-agent system for business and technical requirements analysis with user acceptance test generation.

**Key Features:**
- Analyzes business requirements documents for consistency and completeness
- Checks for conflicting requirements and missing sections
- Generates comprehensive user acceptance test specifications
- Supports IEEE 830 standards and automotive requirements workflows

**Location:** `backend/requirements-agent/`  
**MCP Server:** `mcp-servers/automotive-requirements-mcp/`  
**Documentation:** See [Requirements Analyzer README](backend/requirements-agent/README.md) for detailed setup and usage instructions.

### 3. IDE Integration Support
MCP servers and configuration files for seamless IDE integration with Kiro, Cline, and Amazon Q.
- **Location**: `ide-support/`

## Architecture

Both agents use a **conditional sequential graph** pattern with 2 nodes:

### C Code Analyzer
```
┌─────────────────────┐    Condition: No HIGH     ┌─────────────────────┐
│ Automotive Analyzer │────severity violations───▶│  Unit Test Generator│
│   (Entry Point)     │                           │  (Conditional Node) │
└─────────────────────┘                           └─────────────────────┘
```

### Requirements Analyzer
```
┌─────────────────────────┐                          ┌─────────────────────────────┐
│ Requirements Consistency│─────────────────────────▶│ User Acceptance Test        │
│ Analyzer (Entry Point)  │                          │ Generator                   │
└─────────────────────────┘                          └─────────────────────────────┘
```

**Technical Stack:**
- **Graph Pattern**: Strands GraphBuilder with conditional edges
- **Authentication**: Amazon Cognito with JWT tokens
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Model**: Anthropic Claude Haiku 4.5
- **IDE Integration**: Model Context Protocol (MCP) servers

## Project Structure

```
automotive-strands-agents-in-runtime/
├── backend/                                    # Backend Agent Services
│   ├── c-code-analyzer-agent/                 # C Code Analysis Agent
│   │   ├── sample_automotive_code/            # Sample C code for testing
│   │   │   ├── tests/                         # Generated unit tests
│   │   │   │   ├── test_sample_with_minor_violations.c
│   │   │   │   ├── Makefile
│   │   │   │   └── README.md
│   │   │   ├── sample_with_severe_violations.c
│   │   │   ├── sample_with_minor_violations.c
│   │   │   ├── sample_automotive_compliant.c
│   │   │   └── README.md
│   │   ├── automotive_c_analyzer_notebook.ipynb
│   │   ├── c_code_analyzer.py
│   │   ├── utils.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── requirements-agent/                    # Requirements Analysis Agent
│       ├── automotive_requirements_agent_notebook.ipynb
│       ├── requirements_analyzer.py
│       ├── utils.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── README.md
├── mcp-servers/                               # Model Context Protocol Servers
│   ├── automotive-coding-mcp/                 # C Code Analysis MCP Server
│   │   ├── coding-server.py
│   │   ├── requirements.txt
│   │   └── test_config.py
│   └── automotive-requirements-mcp/           # Requirements Analysis MCP Server
│       ├── requirements-server.py
│       ├── requirements.txt
│       ├── test_config.py
│       └── README.md
├── ide-support/                               # IDE Integration Support
│   ├── kiro/                                  # Kiro IDE Configuration
│   │   ├── settings/mcp.json                  # MCP server configuration
│   │   └── steering/                          # Agent steering rules
│   ├── cline/                                 # Cline IDE Configuration
│   │   └── cline_mcp_settings.json
│   └── .amazonq/                              # Amazon Q Configuration
│       └── agents/
└── weather-app/                               # Sample Requirements Documents
    ├── business-requirements/
    │   └── weather_app_brd.md
    └── technical-requirements/
        ├── weather_app_srs.md
        └── ieee_830_srs_outline.md

## Key Features

### Graph-Based Multi-Agent System
- Uses Strands GraphBuilder for agent orchestration
- Conditional sequential execution pattern with 2-node architecture
- Automatic workflow control based on analysis results
- Performance metrics and execution tracking
- Structured responses with both analysis and generation results

### IDE Integration via MCP
- Real-time analysis directly in your IDE (Kiro, Cline, Amazon Q)
- Automated unit test and UAT generation on-demand
- Continuous automotive coding standards compliance checking
- Seamless integration with development workflows

## Getting Started

### Prerequisites
- Python 3.13+
- AWS credentials configured
- Amazon Bedrock AgentCore SDK access
- UV package manager (for MCP servers): `pip install uv`

### C Code Analyzer Agent

The C Code Analyzer provides automotive C code analysis with custom coding standards compliance checking and automated unit test generation.

**Quick Start:**
```bash
cd backend/c-code-analyzer-agent
pip install -r requirements.txt
jupyter notebook automotive_c_analyzer_notebook.ipynb
```

For detailed setup instructions, sample test cases, and advanced usage, see the [C Code Analyzer README](backend/c-code-analyzer-agent/README.md).

### Requirements Analyzer Agent

The Requirements Analyzer focuses on business and technical requirements analysis with user acceptance test generation.

**Quick Start:**
```bash
cd backend/requirements-agent
pip install -r requirements.txt
jupyter notebook automotive_requirements_agent_notebook.ipynb
```

For detailed setup instructions, path configuration, and troubleshooting, see the [Requirements Analyzer README](backend/requirements-agent/README.md).

### MCP Server Integration for IDEs

#### Kiro IDE Setup
1. Copy MCP configuration:
   ```bash
   cp ide-support/kiro/settings/mcp.json .kiro/settings/mcp.json
   ```
2. Update the configuration with your Python environment path and Cognito client-id
3. Restart Kiro to load the MCP servers

#### Cline IDE Setup
1. Copy MCP configuration:
   ```bash
   cp ide-support/cline/cline_mcp_settings.json ~/.cline/mcp_settings.json
   ```
2. Update paths and credentials as needed

#### Available MCP Tools
- `mcp_automotive_coding_analyze_c_code` - Analyze C code for automotive standards
- `mcp_automotive_requirements_automotive_requirements_analyzer` - Analyze requirements documents

## Sample Test Cases

### C Code Analysis
The C Code Analyzer includes sample automotive C code with varying levels of compliance violations. For detailed information about test cases, generated unit tests, and automotive coding standards, see the [C Code Analyzer README](backend/c-code-analyzer-agent/README.md).

### Requirements Analysis  
The Requirements Analyzer works with sample business and technical requirements documents located in `weather-app/`. For detailed information about requirements analysis workflows and test case generation, see the [Requirements Analyzer README](backend/requirements-agent/README.md).

## Security & Deployment

- **Authentication**: Amazon Cognito with JWT token validation
- **Permissions**: IAM role-based access control
- **Runtime**: Secure deployment on Amazon Bedrock AgentCore Runtime
- **Cleanup**: Optional cleanup procedures for AgentCore instances, ECR repositories, and IAM roles

## Automotive Focus

This system is specifically designed for automotive software development with:
- Safety-critical code analysis and testing standards
- Custom automotive coding standards compliance (AUTO-SAFE-001, AUTO-MEM-001, AUTO-FUNC-001, AUTO-STYLE-001)
- Production-ready deployment architecture
- Integration with automotive development workflows

## MCP Server Integration

### Model Context Protocol (MCP) Servers
The project includes MCP servers for seamless IDE integration:

#### Automotive Coding MCP Server
- **Location**: `mcp-servers/automotive-coding-mcp/`
- **Function**: `mcp_automotive_coding_analyze_c_code`
- **Purpose**: Analyze C code for automotive standards compliance and generate unit tests
- **Usage**: Integrated into IDEs via MCP protocol

#### Automotive Requirements MCP Server  
- **Location**: `mcp-servers/automotive-requirements-mcp/`
- **Function**: `mcp_automotive_requirements_automotive_requirements_analyzer`
- **Purpose**: Analyze requirements documents and generate user acceptance tests
- **Usage**: Integrated into IDEs via MCP protocol

### IDE Support
- **Kiro**: Full MCP integration with steering rules and settings
- **Cline**: MCP configuration for automotive analysis tools
- **Amazon Q**: Agent configuration for automotive workflows

### Benefits of MCP Integration
- **Real-time Analysis**: Analyze code and requirements directly in your IDE
- **Automated Testing**: Generate unit tests and UATs on-demand
- **Standards Compliance**: Continuous automotive coding standards checking
- **Workflow Integration**: Seamless integration with development workflows

## Development Workflow

### Using MCP Tools in IDEs
1. **Code Analysis**: Use `#mcp_automotive_coding_analyze_c_code` in your IDE to analyze C code
2. **Requirements Analysis**: Use `#mcp_automotive_requirements_automotive_requirements_analyzer` for requirements documents

### Testing Your Setup
```bash
# Test C Code Analysis MCP Server
cd mcp-servers/automotive-coding-mcp
python test_config.py

# Test Requirements Analysis MCP Server  
cd mcp-servers/automotive-requirements-mcp
python test_config.py
```

## Next Steps

- **Technical Design Coverage**: Generate/validate technical designs based on requirements
- **Anroid Code Generation Coverage**: Generate code/unit tests for Android. Validate via simulator
