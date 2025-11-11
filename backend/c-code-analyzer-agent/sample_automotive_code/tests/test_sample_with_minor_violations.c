/*
 * Unit Tests for sample_with_minor_violations.c
 * Generated based on automotive coding standards analysis
 * 
 * Test Framework: Unity (or similar C unit testing framework)
 * Compile with: gcc -o test_runner test_sample_with_minor_violations.c ../sample_with_minor_violations.c -DUNIT_TEST
 */

#include <stdio.h>
#include <assert.h>

/* Include the functions under test */
extern int calculate_speed(int distance, int time);
extern int validate_input(int value);
extern int get_engine_temperature(void);

/*
 * Test Suite for calculate_speed function
 */
void test_calculate_speed_normal_case(void) {
    /* Test normal speed calculation */
    int result = calculate_speed(100, 10);
    assert(result == 10);
    printf("PASS: test_calculate_speed_normal_case\n");
}

void test_calculate_speed_zero_time(void) {
    /* Test division by zero handling */
    int result = calculate_speed(100, 0);
    assert(result == -1);
    printf("PASS: test_calculate_speed_zero_time\n");
}

void test_calculate_speed_edge_cases(void) {
    /* Test edge cases */
    assert(calculate_speed(0, 1) == 0);
    assert(calculate_speed(1000, 100) == 10);
    assert(calculate_speed(50, 5) == 10);
    printf("PASS: test_calculate_speed_edge_cases\n");
}

/*
 * Test Suite for validate_input function
 */
void test_validate_input_valid_range(void) {
    /* Test valid input values */
    assert(validate_input(0) == 1);
    assert(validate_input(500) == 1);
    assert(validate_input(1000) == 1);
    printf("PASS: test_validate_input_valid_range\n");
}

void test_validate_input_invalid_range(void) {
    /* Test invalid input values */
    assert(validate_input(-1) == 0);
    assert(validate_input(1001) == 0);
    assert(validate_input(-100) == 0);
    printf("PASS: test_validate_input_invalid_range\n");
}

/*
 * Test Suite for get_engine_temperature function
 */
void test_get_engine_temperature(void) {
    /* Test engine temperature reading */
    int temp = get_engine_temperature();
    assert(temp == 85);
    assert(temp > 0);  /* Temperature should be positive */
    assert(temp < 200); /* Reasonable upper bound for engine temp */
    printf("PASS: test_get_engine_temperature\n");
}

/*
 * Integration Tests
 */
void test_integration_speed_validation(void) {
    /* Test integration between speed calculation and validation */
    int speed = calculate_speed(100, 10);
    int is_valid = validate_input(speed);
    assert(is_valid == 1);
    printf("PASS: test_integration_speed_validation\n");
}

void test_integration_main_workflow(void) {
    /* Test the main workflow integration */
    int speed = calculate_speed(100, 10);
    int is_valid = validate_input(speed);
    int temp = get_engine_temperature();
    
    assert(speed == 10);
    assert(is_valid == 1);
    assert(temp == 85);
    printf("PASS: test_integration_main_workflow\n");
}

/*
 * Test Runner
 */
int main(void) {
    printf("Running Unit Tests for sample_with_minor_violations.c\n");
    printf("=====================================================\n");
    
    /* Run calculate_speed tests */
    printf("\nTesting calculate_speed function:\n");
    test_calculate_speed_normal_case();
    test_calculate_speed_zero_time();
    test_calculate_speed_edge_cases();
    
    /* Run validate_input tests */
    printf("\nTesting validate_input function:\n");
    test_validate_input_valid_range();
    test_validate_input_invalid_range();
    
    /* Run get_engine_temperature tests */
    printf("\nTesting get_engine_temperature function:\n");
    test_get_engine_temperature();
    
    /* Run integration tests */
    printf("\nRunning Integration Tests:\n");
    test_integration_speed_validation();
    test_integration_main_workflow();
    
    printf("\n=====================================================\n");
    printf("All tests completed successfully!\n");
    
    return 0;
}