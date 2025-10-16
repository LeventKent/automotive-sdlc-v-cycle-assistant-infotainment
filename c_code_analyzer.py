from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import re
from datetime import datetime

app = BedrockAgentCoreApp()

# MISRA-C compliance analyzer tool
@tool
def verify_misra_subset_compliance(c_code: str) -> dict:
    """
    Analyze C code for MISRA-C compliance violations ONLY for the rules 8.4, 21.3, 17.7 and 2.2.
    Returns a dictionary with violation severity and details.
    """
    violations = []
    severity_level = "LOW"
    
    # Basic MISRA-C rule checks (simplified for demo)
    misra_rules = {
        "MISRA-C:2012 Rule 8.4": {
            "pattern": r"extern\s+\w+\s+\w+\s*\(",
            "description": "A compatible declaration shall be visible when an object or function with external linkage is defined",
            "severity": "MEDIUM"
        },
        "MISRA-C:2012 Rule 21.3": {
            "pattern": r"\bmalloc\b|\bcalloc\b|\brealloc\b|\bfree\b",
            "description": "The memory allocation and deallocation functions shall not be used",
            "severity": "HIGH"
        },
        "MISRA-C:2012 Rule 17.7": {
            "pattern": r"^\s*\w+\s*\([^)]*\)\s*;",
            "description": "The value returned by a function having non-void return type shall be used",
            "severity": "MEDIUM"
        },
        "MISRA-C:2012 Rule 2.2": {
            "pattern": r"//.*",
            "description": "C++ style comments shall not be used",
            "severity": "LOW"
        }
    }
    
    for rule_id, rule_info in misra_rules.items():
        matches = re.findall(rule_info["pattern"], c_code, re.MULTILINE)
        if matches:
            violations.append({
                "rule": rule_id,
                "description": rule_info["description"],
                "severity": rule_info["severity"],
                "occurrences": len(matches)
            })
            
            # Update overall severity
            if rule_info["severity"] == "HIGH":
                severity_level = "HIGH"
            elif rule_info["severity"] == "MEDIUM" and severity_level != "HIGH":
                severity_level = "MEDIUM"
    
    return {
        "overall_severity": severity_level,
        "violations": violations,
        "total_violations": len(violations),
        "compliant": len(violations) == 0
    }

@tool
def generate_unit_tests(c_code: str, function_name: str = None) -> str:
    """
    Generate unit tests for C code functions.
    """
    # Extract function signatures from C code
    function_pattern = r"(\w+)\s+(\w+)\s*\([^)]*\)\s*{"
    functions = re.findall(function_pattern, c_code)
    
    if not functions:
        return "No functions found in the provided C code."
    
    unit_tests = []
    unit_tests.append("/*")
    unit_tests.append(" * Generated Unit Tests for Automotive C Code")
    unit_tests.append(f" * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    unit_tests.append(" * MISRA-C compliant unit test framework")
    unit_tests.append(" */")
    unit_tests.append("")
    unit_tests.append("#include <stdio.h>")
    unit_tests.append("#include <assert.h>")
    unit_tests.append("#include <string.h>")
    unit_tests.append("")
    unit_tests.append("/* Include your source file here */")
    unit_tests.append("/* #include \"your_source.h\" */")
    unit_tests.append("")
    unit_tests.append("/* Test result counters */")
    unit_tests.append("static int tests_passed = 0;")
    unit_tests.append("static int tests_failed = 0;")
    unit_tests.append("")
    unit_tests.append("/* Test assertion macro */")
    unit_tests.append("#define ASSERT_EQ(expected, actual, test_name) \\")
    unit_tests.append("    do { \\")
    unit_tests.append("        if ((expected) == (actual)) { \\")
    unit_tests.append("            printf(\"PASS: %s\\n\", test_name); \\")
    unit_tests.append("            tests_passed++; \\")
    unit_tests.append("        } else { \\")
    unit_tests.append("            printf(\"FAIL: %s - Expected: %d, Got: %d\\n\", test_name, expected, actual); \\")
    unit_tests.append("            tests_failed++; \\")
    unit_tests.append("        } \\")
    unit_tests.append("    } while(0)")
    unit_tests.append("")
    
    for return_type, func_name in functions:
        if function_name and func_name != function_name:
            continue
            
        unit_tests.append(f"/*")
        unit_tests.append(f" * Test function for {func_name}")
        unit_tests.append(f" */")
        unit_tests.append(f"void test_{func_name}(void) {{")
        unit_tests.append(f"    printf(\"Testing {func_name}...\\n\");")
        unit_tests.append(f"    ")
        unit_tests.append(f"    /* Test case 1: Normal operation */")
        unit_tests.append(f"    /* TODO: Add specific test implementation for {func_name} */")
        unit_tests.append(f"    /* Example: ASSERT_EQ(expected_result, {func_name}(test_params), \"Normal case\"); */")
        unit_tests.append(f"    ")
        unit_tests.append(f"    /* Test case 2: Edge cases */")
        unit_tests.append(f"    /* TODO: Add edge case tests for {func_name} */")
        unit_tests.append(f"    /* Example: ASSERT_EQ(expected_edge_result, {func_name}(edge_params), \"Edge case\"); */")
        unit_tests.append(f"    ")
        unit_tests.append(f"    /* Test case 3: Error conditions */")
        unit_tests.append(f"    /* TODO: Add error condition tests for {func_name} */")
        unit_tests.append(f"    /* Example: ASSERT_EQ(-1, {func_name}(invalid_params), \"Error case\"); */")
        unit_tests.append(f"    ")
        unit_tests.append(f"    printf(\"{func_name} tests completed!\\n\");")
        unit_tests.append("}")
        unit_tests.append("")
    
    unit_tests.append("/*")
    unit_tests.append(" * Main test runner")
    unit_tests.append(" */")
    unit_tests.append("int main(void) {")
    unit_tests.append("    printf(\"Starting Automotive C Code Unit Tests...\\n\");")
    unit_tests.append("    printf(\"==========================================\\n\");")
    unit_tests.append("")
    
    for return_type, func_name in functions:
        if function_name and func_name != function_name:
            continue
        unit_tests.append(f"    test_{func_name}();")
    
    unit_tests.append("")
    unit_tests.append("    printf(\"==========================================\\n\");")
    unit_tests.append("    printf(\"Test Summary:\\n\");")
    unit_tests.append("    printf(\"Tests Passed: %d\\n\", tests_passed);")
    unit_tests.append("    printf(\"Tests Failed: %d\\n\", tests_failed);")
    unit_tests.append("    printf(\"Total Tests: %d\\n\", tests_passed + tests_failed);")
    unit_tests.append("")
    unit_tests.append("    if (tests_failed == 0) {")
    unit_tests.append("        printf(\"All tests PASSED!\\n\");")
    unit_tests.append("        return 0;")
    unit_tests.append("    } else {")
    unit_tests.append("        printf(\"Some tests FAILED!\\n\");")
    unit_tests.append("        return 1;")
    unit_tests.append("    }")
    unit_tests.append("}")
    
    return "\n".join(unit_tests)

# Create the model for all agents
model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
model = BedrockModel(model_id=model_id)

# Create the MISRA compliance analyzer agent
misra_analyzer_agent = Agent(
    name="misra_analyzer",
    model=model,
    tools=[verify_misra_subset_compliance],
    system_prompt="""You are a MISRA-C compliance analyzer for automotive software. Your job is to:
1. Analyze C code for MISRA-C compliance violations (Rules 8.4, 21.3, 17.7, and 2.2)
2. Identify the severity of violations (LOW, MEDIUM, HIGH)
3. Provide detailed explanations of violations found
4. Pass your analysis results to the next stage in the workflow

IMPORTANT: Always use the verify_misra_subset_compliance tool to analyze the code first, then provide your analysis.

In your response, clearly state:
- Overall Severity: [LOW/MEDIUM/HIGH]
- Compliance Status: [COMPLIANT/NON-COMPLIANT]
- Whether the code is suitable for unit test generation

Focus on automotive safety standards and provide clear, actionable feedback."""
)

# Create the unit test generator agent
unit_test_agent = Agent(
    name="unit_test_generator",
    model=model,
    #tools=[generate_unit_tests],
    system_prompt="""You are a unit test generator for C code in automotive applications. Your job is to:
1. Generate comprehensive unit tests for C functions
2. Include edge cases and boundary conditions
3. Follow automotive testing standards
4. Create tests that are suitable for safety-critical applications

Generate clean, well-documented test code that can be easily integrated into a test framework. Always use the generate_unit_tests tool to create the tests."""
)

# Define condition function to check if unit tests should be generated
def should_generate_tests(state):
    """
    Condition function to determine if unit tests should be generated
    based on MISRA analysis results.
    """
    misra_result = state.results.get("misra_analyzer")
    if not misra_result:
        print("DEBUG: No MISRA analyzer result found")
        return False
    
    # Extract the analysis result from the agent's response
    # The misra_result is an AgentResult object, we need to access its .result attribute
    if hasattr(misra_result, 'result'):
        result_text = str(misra_result.result).lower()
    else:
        result_text = str(misra_result).lower()

    
    # Simple approach: Look for HIGH severity violations that should block unit test generation
    # Everything else (LOW, MEDIUM, or COMPLIANT) should allow unit test generation
    
    # Definitive blocking patterns (HIGH severity)
    blocking_patterns = [
        "overall severity**: high",
        "overall severity: high", 
        "**overall severity**: high",
        "severity: high"
    ]

    
    # Check for blocking patterns
    for pattern in blocking_patterns:
        if pattern in result_text:
            print(f"DEBUG: Found blocking pattern: {pattern}")
            return False
        
    # Default: if no blocking patterns found, allow unit test generation
    print("DEBUG: No blocking patterns found, allowing unit test generation")
    return True

# Build the multi-agent graph
def build_automotive_analyzer_graph():
    """
    Build the automotive C code analyzer graph with conditional workflow.
    """
    builder = GraphBuilder()
    
    # Add nodes to the graph
    builder.add_node(misra_analyzer_agent, "misra_analyzer")
    builder.add_node(unit_test_agent, "unit_test_generator")
    
    # Add conditional edge: only generate tests if no severe violations
    builder.add_edge("misra_analyzer", "unit_test_generator", condition=should_generate_tests)
    
    # Set entry point
    builder.set_entry_point("misra_analyzer")
    
    # Build and return the graph
    return builder.build()

# Create the graph instance
automotive_graph = build_automotive_analyzer_graph()

@app.entrypoint
def automotive_c_analyzer(payload):
    """
    Multi-step automotive C code analyzer using agent graph with MISRA compliance check and conditional unit test generation.
    """
    c_code = payload.get("c_code", "")
    if not c_code:
        return {"error": "No C code provided"}
    
    print(f"Analyzing C code: {c_code[:100]}...")
    
    # Create the analysis prompt
    analysis_prompt = f"""Analyze this automotive C code for MISRA-C compliance violations and provide detailed feedback:

{c_code}

Please use the verify_misra_subset_compliance tool to analyze the code and provide a comprehensive report on any violations found."""
    
    # Execute the multi-agent graph
    try:
        graph_result = automotive_graph(analysis_prompt)
        
        print(f"Graph execution completed. Nodes executed: {graph_result.completed_nodes}/{graph_result.total_nodes}")
        print(f"Execution order: {[node.node_id for node in graph_result.execution_order]}")
        
        # Build the response structure
        result = {
            "execution_time_ms": graph_result.execution_time,
            "step1_misra_analysis": {
                "analysis": graph_result.results.get("misra_analyzer", {}).result if graph_result.results.get("misra_analyzer") else "No MISRA analysis performed",
                "violations": "See analysis above for detailed violation information"
            }
        }
        
        # Check if unit tests were generated
        if "unit_test_generator" in graph_result.results:
            result["step2_unit_tests"] = {
                "generated": True,
                "tests": graph_result.results["unit_test_generator"].result
            }
            print("Unit tests generated successfully.")
        else:
            result["step2_unit_tests"] = {
                "generated": False,
                "reason": "Unit test generation was skipped due to severe MISRA-C violations or analysis failure."
            }
            print("Unit test generation was skipped.")
        
        # Return the final result from the graph (last executed node)
        return result
        
    except Exception as e:
        print(f"Error during graph execution: {e}")
        return {
            "error": f"Graph execution failed: {str(e)}",
            "step1_misra_analysis": {"analysis": "Analysis failed", "violations": []},
            "step2_unit_tests": {"generated": False, "reason": "Analysis failed"}
        }

if __name__ == "__main__":
    app.run()