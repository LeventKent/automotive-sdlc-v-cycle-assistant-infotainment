#!/usr/bin/env python3
"""
Simple test to verify the condition function works correctly
"""

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
    
    print(f"DEBUG: Analyzing result text for conditions...")
    print(f"DEBUG: First 300 chars of result: {result_text[:300]}...")
    
    # Simple approach: Look for HIGH severity violations that should block unit test generation
    # Everything else (LOW, MEDIUM, or COMPLIANT) should allow unit test generation
    
    # Definitive blocking patterns (HIGH severity)
    blocking_patterns = [
        "overall severity**: high",
        "overall severity: high", 
        "**overall severity**: high",
        "severity: high"
    ]
    
    # Specific violation patterns (but only if they indicate actual usage, not just mention)
    violation_usage_patterns = [
        "uses malloc",
        "calls malloc", 
        "malloc is used",
        "malloc usage",
        "uses free",
        "calls free",
        "free is used",
        "uses calloc",
        "calls calloc",
        "uses realloc",
        "calls realloc"
    ]
    
    # Check for blocking patterns
    for pattern in blocking_patterns:
        if pattern in result_text:
            print(f"DEBUG: Found blocking pattern: {pattern}")
            return False
    
    # Check for specific violation usage patterns
    for pattern in violation_usage_patterns:
        if pattern in result_text:
            print(f"DEBUG: Found violation usage pattern: {pattern}")
            return False
    
    # If we reach here, no blocking patterns were found
    # Check for positive indicators to be sure
    positive_patterns = [
        "low",
        "medium", 
        "compliant",
        "no violations",
        "suitable for unit test"
    ]
    
    for pattern in positive_patterns:
        if pattern in result_text:
            print(f"DEBUG: Found positive pattern: {pattern}")
            return True
    
    # Default: if no blocking patterns found, allow unit test generation
    print("DEBUG: No blocking patterns found, allowing unit test generation")
    return True

# Mock classes for testing
class MockResult:
    def __init__(self, result_text):
        self.result = result_text

class MockState:
    def __init__(self, result_text):
        self.results = {"misra_analyzer": MockResult(result_text)}

def test_condition_function():
    """Test the condition function with various inputs"""
    
    # Test case from the actual output
    actual_output = """# MISRA-C Compliance Analysis Report

## Summary
- **Overall Severity**: LOW
- **Total Violations Found**: 0
- **Compliance Status**: COMPLIANT

## Detailed Analysis

The provided code was analyzed for compliance with MISRA-C:2012 rules 8.4, 21.3, 17.7, and 2.2. No violations were detected in the code.

### MISRA-C:2012 Rule 8.4 - Compliance
- **Rule Description**: A compatible declaration shall be visible when an object or function with external linkage is defined.
- **Status**: COMPLIANT
- **Analysis**: All functions and variables are properly defined with consistent declarations.

### MISRA-C:2012 Rule 21.3 - Compliance
- **Rule Description**: The memory allocation and deallocation functions shall not be used.
- **Status**: COMPLIANT
- **Analysis**: The code does not use any dynamic memory allocation functions like malloc(), calloc(), realloc(), or free().

### MISRA-C:2012 Rule 17.7 - Compliance
- **Rule Description**: The value returned by a function having non-void return type shall be used.
- **Status**: COMPLIANT
- **Analysis**: All return values from functions are properly used. Additionally, the printf() function calls are properly cast to void using (void)printf(...) to explicitly indicate that the return value is intentionally ignored.

### MISRA-C:2012 Rule 2.2 - Compliance
- **Rule Description**: C++ style comments shall not be used.
- **Status**: COMPLIANT
- **Analysis**: The code exclusively uses C-style comments (/* ... */) and avoids C++ style comments (//), which is in compliance with MISRA-C:2012 guidelines.

## Notable Compliance Features

The code demonstrates excellent MISRA-C compliance through these practices:

1. **Proper Function Declarations**: Functions that take no parameters are explicitly declared with (void) rather than empty parentheses, which is good practice for MISRA-C.

2. **Explicit Comparison with Constants**: Comparisons are done explicitly (e.g., `if (is_valid != 0)` rather than `if (is_valid)`), which follows MISRA-C recommendation for clear and unambiguous code.

3. **Careful Error Handling**: The code properly handles error conditions (e.g., division by zero check in calculate_speed).

4. **Well-Structured Code**: Clear organization with comprehensive function documentation including purpose, parameters, and return values.

5. **Explicit Void Casting**: The code explicitly casts printf() return values to void, acknowledging that the return value is intentionally unused.

6. **Proper Use of Parentheses**: Compound conditions in if statements use appropriate parentheses to avoid potential confusion or precedence issues.

## Conclusion

This code is fully compliant with the specified MISRA-C:2012 rules (8.4, 21.3, 17.7, and 2.2). It demonstrates good coding practices for automotive safety-critical applications and is suitable for unit test generation. The code follows defensive programming practices, has clear structure, and properly handles error conditions. No modifications are required to achieve compliance with the specified subset of MISRA-C rules."""

    test_cases = [
        {
            "name": "Actual compliant output",
            "text": actual_output,
            "expected": True
        },
        {
            "name": "High severity violations",
            "text": "Overall Severity: HIGH\nSevere violations found with malloc usage",
            "expected": False
        },
        {
            "name": "Medium severity violations",
            "text": "Overall Severity: MEDIUM\nSome violations found but no severe issues",
            "expected": True
        },
        {
            "name": "Code that actually uses malloc",
            "text": "The code uses malloc for dynamic memory allocation which violates MISRA-C rules",
            "expected": False
        }
    ]
    
    print("Testing condition function...")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print("-" * 40)
        state = MockState(test_case["text"])
        result = should_generate_tests(state)
        status = "✅ PASS" if result == test_case["expected"] else "❌ FAIL"
        print(f"{status} Expected {test_case['expected']}, Got {result}")
    
    return True

if __name__ == "__main__":
    test_condition_function()