# Automotive Multi-Agent Analysis System

This project implements multiple multi-agent systems for automotive software development using Strands agents deployed on Amazon Bedrock AgentCore Runtime with inbound authentication.

## Components

### 1. C Code Analyzer (Main Directory)
Multi-agent system for automotive C code analysis with MISRA-C compliance checking and unit test generation.

### 2. Requirements Analyzer (Backend Directory)
Multi-agent system for business requirements analysis and user acceptance test generation.

## Overview

The system uses a **conditional sequential graph** pattern with 2 nodes:

1. **MISRA-C Compliance Analysis**: Analyzes C code for MISRA-C compliance violations
2. **Unit Test Generation**: If no severe violations are found, generates comprehensive unit tests

## Architecture

```
┌─────────────────────┐    Condition: No HIGH     ┌─────────────────────┐
│   MISRA Analyzer    │────severity violations───▶│  Unit Test Generator│
│   (Entry Point)     │                           │  (Conditional Node) │
└─────────────────────┘                           └─────────────────────┘
```

- **Node 1**: MISRA-C Compliance Analyzer - Identifies safety-critical violations (Entry Point)
- **Node 2**: Unit Test Generator - Creates automotive-grade unit tests (Conditional Execution)
- **Graph Pattern**: Strands GraphBuilder with conditional edges
- **Authentication**: Amazon Cognito with JWT tokens
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Model**: Anthropic Claude Sonnet 4.5

## Project Structure

```
automotive-strands-agents-in-runtime/
├── backend/                                    # Requirements Analyzer Backend
│   ├── automotive_requirements_agent_notebook.ipynb
│   ├── requirements_analyzer.py
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
│   └── sample_misra_compliant.c
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

### MISRA-C Compliance Checking
- Detects common MISRA-C:2012 rule violations
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
- Automatic workflow control based on MISRA violation severity

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
3. **Compliant Code** (`sample_misra_compliant.c`): MISRA-compliant C code (generates comprehensive unit tests)

Generated unit tests are returned as part of the agent response and can be saved manually if needed.

## MISRA-C Rules Checked

- **Rule 2.2**: C++ style comments shall not be used
- **Rule 8.4**: Compatible declaration visibility for external linkage
- **Rule 17.7**: Return value usage for non-void functions
- **Rule 21.3**: Memory allocation/deallocation functions shall not be used

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
- MISRA-C compliance checking
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
See `backend/README.md` for detailed instructions on running the requirements analyzer.

## Next Steps

- Extend MISRA-C rule coverage
- Add support for additional automotive standards (ISO 26262)
- Integrate requirements and C code analysis workflows
- Add integration with automotive CI/CD pipelines
- Expand business requirements analysis capabilities