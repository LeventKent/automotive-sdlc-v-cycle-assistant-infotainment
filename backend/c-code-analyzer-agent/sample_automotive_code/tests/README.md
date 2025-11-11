# Unit Tests for Automotive C Code

This directory contains unit tests for the automotive C code samples, generated based on automotive coding standards analysis.

## Test Coverage

### `test_sample_with_minor_violations.c`
Tests for `sample_with_minor_violations.c` which contains:
- **calculate_speed()** - Vehicle speed calculation with error handling
- **validate_input()** - Input validation for automotive sensors  
- **get_engine_temperature()** - Engine temperature simulation
- **Integration tests** - Combined workflow testing

## Running Tests

### Quick Start
```bash
cd tests
make test
```

### Manual Compilation
```bash
gcc -Wall -Wextra -std=c99 -DUNIT_TEST -o test_runner test_sample_with_minor_violations.c ../sample_with_minor_violations.c
./test_runner
```

## Test Framework

The tests use a simple assertion-based approach. For more advanced testing, consider integrating with:
- **Unity** - Lightweight C testing framework
- **CMocka** - Unit testing framework with mock support
- **CppUTest** - C/C++ unit testing framework

## Automotive Coding Standards

These tests verify compliance with custom automotive coding standards:
- **AUTO-SAFE-001** - Safety-critical function validation
- **AUTO-MEM-001** - Memory management compliance
- **AUTO-FUNC-001** - Function design standards
- **AUTO-STYLE-001** - Code style and documentation

## Test Categories

1. **Unit Tests** - Individual function testing
2. **Integration Tests** - Component interaction testing
3. **Edge Case Tests** - Boundary condition validation
4. **Error Handling Tests** - Fault tolerance verification

## Expected Output

```
Running Unit Tests for sample_with_minor_violations.c
=====================================================

Testing calculate_speed function:
PASS: test_calculate_speed_normal_case
PASS: test_calculate_speed_zero_time
PASS: test_calculate_speed_edge_cases

Testing validate_input function:
PASS: test_validate_input_valid_range
PASS: test_validate_input_invalid_range

Testing get_engine_temperature function:
PASS: test_get_engine_temperature

Running Integration Tests:
PASS: test_integration_speed_validation
PASS: test_integration_main_workflow

=====================================================
All tests completed successfully!
```