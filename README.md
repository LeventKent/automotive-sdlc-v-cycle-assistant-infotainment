# Automotive C Code Analyzer with Strands Agents

This project implements a multi-agent system for automotive C code analysis using Strands agents deployed on Amazon Bedrock AgentCore Runtime with inbound authentication.

## Overview

The system uses a **conditional sequential graph** pattern with 2 nodes:

1. **MISRA-C Compliance Analysis**: Analyzes C code for MISRA-C compliance violations
2. **Unit Test Generation**: If no severe violations are found, generates comprehensive unit tests

## Architecture

```
┌─────────────────────┐    Condition: No HIGH    ┌─────────────────────┐
│   MISRA Analyzer    │────severity violations───▶│  Unit Test Generator │
│   (Entry Point)     │                          │  (Conditional Node)  │
└─────────────────────┘                          └─────────────────────┘
```

- **Node 1**: MISRA-C Compliance Analyzer - Identifies safety-critical violations (Entry Point)
- **Node 2**: Unit Test Generator - Creates automotive-grade unit tests (Conditional Execution)
- **Graph Pattern**: Strands GraphBuilder with conditional edges
- **Authentication**: Amazon Cognito with JWT tokens
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Model**: Anthropic Claude Sonnet 3.7

## Files

- `c_code_analyzer.py` - Main agent implementation with multi-agent workflow
- `utils.py` - Utility functions for Cognito setup and IAM role creation
- `automotive_c_analyzer_notebook.ipynb` - Jupyter notebook with complete tutorial
- `requirements.txt` - Python dependencies
- `sample_automotive_code/` - Directory containing sample C code for testing
  - `sample_with_severe_violations.c` - C code with high-severity MISRA violations
  - `sample_with_minor_violations.c` - C code with minor MISRA violations
  - `sample_misra_compliant.c` - MISRA-C compliant automotive code

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

1. **Prerequisites**:
   - Python 3.13+
   - AWS credentials configured
   - Docker running
   - Amazon Bedrock AgentCore SDK access

2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Jupyter Notebook**:
   ```bash
   jupyter notebook automotive_c_analyzer_notebook.ipynb
   ```

4. **Follow the notebook steps**:
   - Set up Cognito authentication
   - Configure and deploy the agent
   - Test with sample C code

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

## Next Steps

- Extend MISRA-C rule coverage
- Add support for additional automotive standards (ISO 26262)
- Implement more sophisticated unit test patterns
- Add integration with automotive CI/CD pipelines