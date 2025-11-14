# Design Agent MCP Tool Usage

## Overview

The Software Design Agent MCP tool (`mcp_automotive_design_automotive_design_generator`) generates comprehensive technical design documents from validated requirements. It uses a multi-agent workflow with conditional validation to ensure design completeness and quality.

## When to Use This Tool

Use the Design Agent when you need to:
- Transform validated requirements into technical design documents
- Generate architecture diagrams and component specifications
- Define interfaces, data models, and implementation guidance
- Ensure alignment with automotive safety standards (ISO 26262)
- Bridge the gap between requirements and code implementation

## Tool Signature

```
mcp_automotive_design_automotive_design_generator(requirements_docs: str) -> dict
```

## Input Format

The tool accepts a single parameter:

- **requirements_docs** (string, required): The complete validated requirements document content

The requirements document should include:
- Introduction and glossary
- User stories with acceptance criteria
- Functional and non-functional requirements
- Automotive standards references (ISO 26262, UNECE WP.29, etc.)

## Output Format

The tool returns a dictionary with the following structure:

```json
{
  "execution_time_ms": 1234,
  "step1_design_generation": {
    "design": "Complete technical design document with architecture, components, interfaces, data models, safety considerations, and implementation guidance",
    "completeness_analysis": "Analysis of design coverage including severity levels and identified issues"
  },
  "step2_design_validation": {
    "validated": true,
    "validation_report": "Design validation results with quality assessment and recommendations",
    "quality_score": 85
  }
}
```

### Response Fields

#### execution_time_ms
Total execution time for the complete workflow in milliseconds.

#### step1_design_generation
Contains the generated design and completeness analysis:
- **design**: The complete technical design document including:
  - Architecture Overview
  - Component Specifications
  - Interface Definitions
  - Data Models
  - Safety Considerations
  - Implementation Guidance
  - Testing Strategy

- **completeness_analysis**: Analysis results showing:
  - Overall severity (LOW, MEDIUM, HIGH)
  - List of identified issues with descriptions
  - Total issue count
  - Ready for validation flag
  - Severity counts breakdown

#### step2_design_validation
Contains validation results (only present if design has no HIGH severity issues):
- **validated**: Boolean indicating if validation was performed
- **validation_report**: Detailed validation results including:
  - Architecture assessment
  - Requirements coverage verification
  - Risk analysis
  - Recommendations for improvement
- **quality_score**: Overall design quality rating (0-100)

**Note**: If the design has HIGH severity completeness issues, the validation step is skipped and step2_design_validation will indicate this.

## Usage Examples

### Example 1: Generate Design from Weather App Requirements

```python
# Read the validated requirements document
with open('weather-app/technical-requirements/weather_app_srs.md', 'r') as f:
    requirements = f.read()

# Call the design generator tool
result = mcp_automotive_design_automotive_design_generator(
    requirements_docs=requirements
)

# Check execution results
print(f"Execution time: {result['execution_time_ms']}ms")

# Review the generated design
design = result['step1_design_generation']['design']
print("Generated Design:")
print(design)

# Check completeness analysis
analysis = result['step1_design_generation']['completeness_analysis']
print(f"\nDesign Completeness: {analysis}")

# Review validation results (if performed)
if 'step2_design_validation' in result and result['step2_design_validation']['validated']:
    validation = result['step2_design_validation']
    print(f"\nQuality Score: {validation['quality_score']}")
    print(f"Validation Report:\n{validation['validation_report']}")
else:
    print("\nValidation was skipped due to HIGH severity completeness issues")
```

### Example 2: Generate Design from Requirements String

```python
requirements_text = """
# Requirements Document

## Introduction
This system provides real-time vehicle diagnostics and monitoring.

## Glossary
- **ECU**: Electronic Control Unit
- **CAN Bus**: Controller Area Network communication protocol

## Requirements

### Requirement 1
**User Story:** As a vehicle technician, I want to monitor ECU status in real-time, so that I can diagnose issues quickly

#### Acceptance Criteria
1. WHEN the diagnostic tool connects to the vehicle, THE System SHALL retrieve ECU status data via CAN Bus
2. THE System SHALL display ECU status with update frequency of 100 milliseconds or less
3. IF communication with an ECU fails, THEN THE System SHALL display an error indicator within 500 milliseconds
"""

# Generate design
result = mcp_automotive_design_automotive_design_generator(
    requirements_docs=requirements_text
)

# Extract and save the design
design_doc = result['step1_design_generation']['design']
with open('technical_design.md', 'w') as f:
    f.write(design_doc)
```

### Example 3: Handling Incomplete Designs

```python
# Generate design from incomplete requirements
result = mcp_automotive_design_automotive_design_generator(
    requirements_docs=incomplete_requirements
)

# Check completeness analysis
analysis = result['step1_design_generation']['completeness_analysis']

# Parse the analysis to identify issues
if "HIGH" in analysis:
    print("⚠️ Design has HIGH severity issues - validation was skipped")
    print("Issues to address:")
    # Extract and display specific issues from the analysis
    print(analysis)
    
    # The design is still generated but needs refinement
    design = result['step1_design_generation']['design']
    print("\nPartial design generated:")
    print(design)
else:
    print("✓ Design is complete and validated")
    validation = result['step2_design_validation']
    print(f"Quality Score: {validation['quality_score']}")
```

## Interpreting Results

### Design Completeness Severity Levels

- **LOW**: Minor issues that don't block implementation (e.g., missing testing strategy)
- **MEDIUM**: Important issues that should be addressed (e.g., incomplete error handling)
- **HIGH**: Critical issues that block validation (e.g., missing architecture, missing safety considerations)

### Validation Quality Score

The quality score (0-100) indicates overall design quality:
- **90-100**: Excellent - Ready for implementation
- **80-89**: Good - Minor improvements recommended
- **70-79**: Acceptable - Some improvements needed
- **Below 70**: Needs significant improvement

### Common Design Issues

1. **Missing Architecture Section**: Add high-level system architecture overview
2. **Missing Component Specifications**: Define all components with clear responsibilities
3. **Missing Interface Definitions**: Specify APIs, protocols, and data contracts
4. **Missing Safety Considerations**: Address ISO 26262 compliance and risk mitigation
5. **Incomplete Implementation Guidance**: Provide step-by-step development approach

## Workflow Integration

The Design Agent fits into the automotive software development workflow:

1. **Requirements Analysis** → Use `mcp_automotive_requirements_automotive_requirements_analyzer`
2. **Design Generation** → Use `mcp_automotive_design_automotive_design_generator` (this tool)
3. **Code Implementation** → Implement based on generated design
4. **Code Analysis** → Use `mcp_automotive_coding_analyze_c_code` (C Code Analyzer)

## Best Practices

1. **Always start with validated requirements**: Use the Requirements Analyzer first to ensure requirements are complete and compliant with EARS/INCOSE standards

2. **Review completeness analysis**: Check the completeness analysis before proceeding to implementation. Address HIGH severity issues by refining requirements

3. **Use validation results**: If validation is performed, review the quality score and recommendations to improve the design

4. **Iterate as needed**: If the design has issues, refine the requirements and regenerate the design

5. **Save design artifacts**: Store the generated design document for reference during implementation

6. **Reference requirements**: The design will reference specific requirements - maintain traceability throughout implementation

## Troubleshooting

### Issue: Validation is always skipped
**Cause**: Design has HIGH severity completeness issues
**Solution**: Review the completeness analysis, identify missing sections, and enhance the requirements document

### Issue: Low quality score
**Cause**: Design doesn't fully address requirements or has architectural issues
**Solution**: Review validation recommendations and refine the design by improving requirements clarity

### Issue: Missing safety considerations
**Cause**: Requirements don't specify safety-critical aspects
**Solution**: Add safety requirements with ISO 26262 references in the requirements document

### Issue: Incomplete component specifications
**Cause**: Requirements lack sufficient detail about system components
**Solution**: Add more detailed functional requirements for each component

## Configuration

The MCP server is configured in `ide-support/kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "automotive-design": {
      "command": "./.venv/bin/python",
      "args": [
        "automotive-strands-agents-in-runtime/mcp-servers/automotive-design-mcp/design-server.py"
      ],
      "env": {
        "AWS_REGION": "us-west-2",
        "FASTMCP_LOG_LEVEL": "INFO",
        "COGNITO_CLIENT_ID": "your-cognito-client-id",
        "COGNITO_USERNAME": "testuser",
        "COGNITO_PASSWORD": "MyPassword123!"
      },
      "disabled": false,
      "autoApprove": [
        "automotive_design_generator"
      ]
    }
  }
}
```

Update the `COGNITO_CLIENT_ID` with your actual Cognito client ID from the deployment notebook.

## Related Documentation

- Requirements Agent: `ide-support/kiro/steering/requirements-agent-mcp-tool-use.md`
- C Code Analyzer: `ide-support/kiro/steering/analyze-c-code-mcp-tool-use.md`
- Design Agent Backend: `backend/design-agent/README.md`
- MCP Server: `mcp-servers/automotive-design-mcp/README.md`
