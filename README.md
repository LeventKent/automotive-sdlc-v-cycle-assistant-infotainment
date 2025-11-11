# Automotive Multi-Agent Analysis System

This project implements multiple multi-agent systems for automotive software development using Strands agents deployed on Amazon Bedrock AgentCore Runtime with inbound authentication.

## Components

### 1. C Code Analyzer (Main Directory)
Multi-agent system for automotive C code analysis with custom automotive coding standards compliance checking and unit test generation.

### 2. Requirements Analyzer (Backend Directory)
Multi-agent system for business requirements analysis and user acceptance test generation.

## Overview

The system uses a **conditional sequential graph** pattern with 2 nodes:

1. **Automotive Coding Standards Analysis**: Analyzes C code for custom automotive coding standards violations
2. **Unit Test Generation**: If no severe violations are found, generates comprehensive unit tests

## Architecture

```
┌─────────────────────┐    Condition: No HIGH     ┌─────────────────────┐
│ Automotive Analyzer │────severity violations───▶│  Unit Test Generator│
│   (Entry Point)     │                           │  (Conditional Node) │
└─────────────────────┘                           └─────────────────────┘
```

- **Node 1**: Automotive Coding Standards Analyzer - Identifies safety-critical violations (Entry Point)
- **Node 2**: Unit Test Generator - Creates automotive-grade unit tests (Conditional Execution)
- **Graph Pattern**: Strands GraphBuilder with conditional edges
- **Authentication**: Amazon Cognito with JWT tokens
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Model**: Anthropic Claude Sonnet 4.5

## Project Structure

```
automotive-strands-agents-in-runtime/
├── backend/                                    # Backend Services
│   └── requirements-agent/                    # Requirements Analyzer Backend
│       ├── automotive_requirements_agent_notebook.ipynb
│       ├── requirements_analyzer.py
│   ├── utils.py
│   ├── requirements.txt
│   └── README.md
├── c_code_analyzer.py                          # C Code Analyzer (main directory)
├── automotive_c_analyzer_notebook.ipynb       # C Code Analysis Tutorial
├── utils.py                                   # Shared utilities
├── requirements.txt                           # Main dependencies
├── sample_automotive_code/                    # Sample C code for testing
│   ├── sample_with_severe_violations.c
│   ├── sample_with_minor_violations.c
│   └── sample_automotive_compliant.c
├── requirements/weather-app/                  # Requirements documents
│   ├── business/weather_app_brd.md
│   └── technical/weather_app_srs.md
└── tests/                                     # Generated test files
    └── test_speed_calculator.c

## Key Features

### Graph-Based Multi-Agent System
- Uses Strands GraphBuilder for agent orchestration
- Conditional sequential execution pattern
- Automatic workflow control based on analysis results
- Performance metrics and execution tracking

### Automotive Coding Standards Compliance Checking
- Detects custom automotive coding standards violations
- Categorizes violations by severity (LOW, MEDIUM, HIGH)
- Focuses on automotive safety standards
- Prevents unit test generation for code with severe violations

### Unit Test Generation
- Generates comprehensive unit tests for C functions
- Includes edge cases and boundary conditions
- Follows automotive testing standards
- Creates tests suitable for safety-critical applications
- Returns generated tests as response content
- Includes test result tracking and assertion macros

### Multi-Agent Graph Workflow
- Conditional execution based on compliance analysis results using GraphBuilder
- Structured response with both analysis and test generation results
- Clear separation of concerns between graph nodes
- Execution metrics and performance tracking
- Automatic workflow control based on automotive coding standards violation severity

## Getting Started

### C Code Analyzer (Main Directory)

1. **Prerequisites**:
   - Python 3.13+
   - AWS credentials configured
   - Amazon Bedrock AgentCore SDK access

2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the C Code Analysis Notebook**:
   ```bash
   jupyter notebook automotive_c_analyzer_notebook.ipynb
   ```

### Requirements Analyzer (Backend Directory)

1. **Navigate to backend**:
   ```bash
   cd backend
   ```

2. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Requirements Analysis Notebook**:
   ```bash
   jupyter notebook automotive_requirements_agent_notebook.ipynb
   ```

### MCP Configuration for IDEs

- Take applicable mcp.json file under `ide-support` and put it to the expected path of your IDE
  - For Kiro: .kiro/settings/mcp.json
- Set path to your local python environment in mcp.json
- Set Cognito client-id in mcp.json

## Sample Test Cases

The notebook includes three test cases using files from `sample_automotive_code/`:

1. **Severe Violations** (`sample_with_severe_violations.c`): C code with malloc/free usage (blocks unit test generation)
2. **Minor Violations** (`sample_with_minor_violations.c`): C code with C++ style comments (allows unit test generation)
3. **Compliant Code** (`sample_automotive_compliant.c`): Automotive-compliant C code (generates comprehensive unit tests)

Generated unit tests are returned as part of the agent response and can be saved manually if needed.

## Custom Automotive Coding Standards Checked

- **AUTO-STYLE-001**: Use C-style comments for better compiler compatibility across automotive toolchains
- **AUTO-SAFE-001**: External function declarations must be visible at definition point for safety traceability
- **AUTO-FUNC-001**: Function return values must be checked for error handling in automotive systems
- **AUTO-MEM-001**: Dynamic memory allocation is prohibited in safety-critical automotive systems

## Security

- Inbound authentication using Amazon Cognito
- JWT token validation
- IAM role-based permissions
- Secure deployment on AgentCore Runtime

## Cleanup

The notebook includes optional cleanup code to remove:
- AgentCore Runtime instances
- ECR repositories
- IAM roles (manual cleanup may be required)

## Automotive Focus

This implementation is specifically designed for automotive software development with:
- Safety-critical code analysis
- Custom automotive coding standards compliance checking
- Automotive testing standards
- Production-ready deployment architecture

## Requirements Analyzer (Backend)

The backend directory contains a separate multi-agent system for business requirements analysis:

### Features
- **Business Requirements Focus**: Analyzes documents from `requirements/weather-app/business/`
- **Consistency Analysis**: Checks for conflicting business requirements
- **Completeness Assessment**: Identifies missing business sections
- **User Acceptance Test Generation**: Creates business-focused test specifications
- **Conditional Execution**: Only generates tests when quality standards are met

### Architecture
```
┌─────────────────────────┐    Condition: No HIGH    ┌─────────────────────────────┐
│ Requirements Consistency │────severity violations───▶│ User Acceptance Test        │
│ Analyzer (Entry Point)  │                          │ Generator (Conditional Node)│
└─────────────────────────┘                          └─────────────────────────────┘
```

### Usage
See `backend/requirements-agent/README.md` for detailed instructions on running the requirements analyzer.

## Next Steps

- Extend custom automotive coding standards rule coverage
- Add support for additional automotive standards (ISO 26262)
- Integrate requirements and C code analysis workflows
- Add integration with automotive CI/CD pipelines
- Expand business requirements analysis capabilities