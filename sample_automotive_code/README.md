# Sample Automotive C Code

This directory contains sample C code files for testing the automotive MISRA-C analyzer and unit test generator.

## Sample Files

### Input Files (C Code Samples)

1. **`sample_with_severe_violations.c`**
   - Contains high-severity MISRA-C violations
   - Includes malloc/free usage (Rule 21.3)
   - Should block unit test generation
   - Used to demonstrate severe violation handling

2. **`sample_with_minor_violations.c`**
   - Contains only minor MISRA-C violations
   - Includes C++ style comments (Rule 2.2)
   - Should allow unit test generation
   - Used to demonstrate conditional workflow

3. **`sample_misra_compliant.c`**
   - Fully MISRA-C:2012 compliant code
   - Uses proper C-style comments
   - Follows automotive coding standards
   - Should generate comprehensive unit tests

### Output (Generated Unit Tests)

Unit tests are generated as response content when MISRA analysis passes (no severe violations):
- Comprehensive test framework with automotive-grade patterns
- Test result tracking and assertion macros
- MISRA-C compliant test code structure
- Ready-to-compile C test files

## MISRA-C Rules Demonstrated

- **Rule 2.2**: C++ style comments shall not be used
- **Rule 8.4**: Compatible declaration visibility for external linkage
- **Rule 17.7**: Return value usage for non-void functions
- **Rule 21.3**: Memory allocation/deallocation functions shall not be used

## Usage

These files are automatically loaded by the Jupyter notebook during testing. The agent system:

1. Analyzes each sample file for MISRA-C compliance
2. Categorizes violations by severity (LOW, MEDIUM, HIGH)
3. Generates unit tests only if no HIGH severity violations are found
4. Returns generated unit tests as part of the agent response

## Automotive Context

All sample code represents typical automotive software patterns:
- Vehicle speed calculations
- Sensor data processing
- Input validation for safety-critical systems
- Engine temperature monitoring
- Error handling for fault tolerance

The generated unit tests follow automotive testing standards suitable for safety-critical applications.