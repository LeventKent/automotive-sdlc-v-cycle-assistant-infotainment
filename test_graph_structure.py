#!/usr/bin/env python3
"""
Simple test to verify the graph structure works correctly
"""

from c_code_analyzer import automotive_graph, should_generate_tests

def test_condition_function():
    """Test the condition function logic"""
    
    # Mock state object for testing
    class MockResult:
        def __init__(self, result_text):
            self.result = result_text
    
    class MockState:
        def __init__(self, result_text):
            self.results = {"misra_analyzer": MockResult(result_text)}
    
    # Test cases
    test_cases = [
        {
            "name": "Compliant code",
            "text": "Overall Severity: LOW\nCompliance Status: COMPLIANT\nNo violations found",
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
        }
    ]
    
    print("Testing condition function...")
    print("=" * 50)
    
    for test_case in test_cases:
        state = MockState(test_case["text"])
        result = should_generate_tests(state)
        status = "✅ PASS" if result == test_case["expected"] else "❌ FAIL"
        print(f"{status} {test_case['name']}: Expected {test_case['expected']}, Got {result}")
    
    return True

def test_graph_structure():
    """Test that the graph is properly constructed"""
    
    # Test with compliant code (should execute both nodes)
    compliant_code = """
#include <stdio.h>

/* MISRA-compliant C style comment */
int calculate_speed(int distance, int time) {
    int result;
    if (time == 0) {
        result = -1; /* Error case */
    } else {
        result = distance / time;
    }
    return result;
}

int main(void) {
    int speed = calculate_speed(100, 10);
    (void)printf("Speed: %d\\n", speed);
    return 0;
}
"""
    
    print("\nTesting graph with MISRA-compliant code...")
    print("=" * 50)
    
    try:
        result = automotive_graph(f"Analyze this C code for MISRA-C compliance:\n\n{compliant_code}")
        
        print(f"Graph execution completed!")
        print(f"Total nodes: {result.total_nodes}")
        print(f"Completed nodes: {result.completed_nodes}")
        print(f"Failed nodes: {result.failed_nodes}")
        print(f"Execution time: {result.execution_time}ms")
        
        print("\nExecution order:")
        for node in result.execution_order:
            print(f"  - {node.node_id}")
        
        print("\nNode results:")
        for node_id, node_result in result.results.items():
            print(f"  {node_id}: {'Success' if node_result else 'Failed'}")
        
        # Check if unit tests were generated
        if "unit_test_generator" in result.results:
            print("\n✅ Unit tests were generated!")
            return True
        else:
            print("\n❌ Unit tests were NOT generated!")
            return False
        
    except Exception as e:
        print(f"Error during graph execution: {e}")
        return False

if __name__ == "__main__":
    # Test condition function first
    test_condition_function()
    
    # Then test full graph
    success = test_graph_structure()
    if success:
        print("\n✅ Graph structure test completed successfully!")
    else:
        print("\n❌ Graph structure test failed!")