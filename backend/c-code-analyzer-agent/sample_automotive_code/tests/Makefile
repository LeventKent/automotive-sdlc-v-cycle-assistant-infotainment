# Makefile for Automotive C Code Unit Tests
# Supports automotive coding standards compliance

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -DUNIT_TEST
TARGET = test_runner
SOURCE_DIR = ..
TEST_DIR = .

# Source files
SOURCES = $(SOURCE_DIR)/sample_with_minor_violations.c
TEST_SOURCES = test_sample_with_minor_violations.c

# Object files
OBJECTS = $(SOURCES:.c=.o)
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)

# Default target
all: $(TARGET)

# Build the test runner
$(TARGET): $(TEST_OBJECTS) $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(TEST_OBJECTS) $(OBJECTS)

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Run tests
test: $(TARGET)
	./$(TARGET)

# Clean build artifacts
clean:
	rm -f $(TARGET) $(TEST_OBJECTS) $(OBJECTS)

# Install dependencies (if using Unity framework)
install-unity:
	@echo "To use Unity testing framework:"
	@echo "1. Download Unity from: https://github.com/ThrowTheSwitch/Unity"
	@echo "2. Place unity.c and unity.h in this directory"
	@echo "3. Update CFLAGS to include Unity"

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the test runner"
	@echo "  test    - Build and run tests"
	@echo "  clean   - Remove build artifacts"
	@echo "  help    - Show this help message"

.PHONY: all test clean install-unity help