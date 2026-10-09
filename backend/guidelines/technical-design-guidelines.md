# Technical Design Guidelines for Automotive Applications

## Overview

This document provides simple guidelines for creating technical design documents that align with automotive safety standards and development best practices.

## Ground Rules

- **The requirements are the only source of facts.** Classifications, targets, constraints, deadlines and budgets come from the provided requirements documents (BRD, SRS and supporting documents). Copy them exactly, including wording such as "prior to SOP".
- **Mark everything else.** If the design needs a value the requirements do not give, label it as a proposal or an assumption and list it under open issues. Never present an invented value as a requirement.
- **No code.** The design describes architecture and behavior in prose, tables and diagrams. Do not include source code, build scripts, method signatures in a programming language, or JSON payload examples. Diagrams may use Mermaid.

## Document Structure

### 1. Executive Summary
- **Purpose**: Brief overview of the application and key objectives
- **Key Requirements**: Safety classification as stated in the requirements, performance targets from the requirements, platform constraints
- **Project Constraints**: Team size, timeline, budget, testing resources, exactly as stated in the requirements

### 2. Architecture Overview
- **High-Level Diagram**: Visual representation of system components
- **Component Layers**: UI Layer, Business Logic Layer, Data Layer
- **External Interfaces**: APIs, vehicle systems, middleware services

### 3. Component Specifications
Each component should include:
- **Component ID**: Unique identifier
- **Purpose**: What the component does
- **Responsibilities**: Key functions and duties
- **Dependencies**: Other components it relies on
- **Performance Targets**: Response time, memory usage, etc., traced to the requirement they come from

### 4. Safety Considerations
For automotive applications, include:
- **Safety Classification (ISO 26262)**: Carry over ASIL/QM allocations exactly as stated in the requirements (HARA, safety goals, safety requirements). Never assign, raise or lower an ASIL yourself. If the requirements allocate none, state "No ASIL allocated in the provided requirements; treated as QM pending HARA" and list the safety-relevant functions as input for the HARA.
- **Freedom from Interference**: Where ASIL and QM parts coexist, describe how QM parts cannot delay or corrupt the safety-related path.
- **Failure Modes**: What can go wrong and how to handle it
- **Driver Distraction**: Minimize interactions while driving
- **Error Recovery**: Graceful degradation strategies

### 5. Implementation Guidance
- **Development Phases**: Break work into manageable phases that fit the timeline in the requirements
- **Key Technologies**: Programming languages, frameworks, libraries
- **Build Configuration**: Build variants and key dependencies, described in prose (no build scripts)
- **Project Structure**: File organization and naming conventions

## Design Principles

### Safety First
- Use only safety classifications given in the requirements; mark anything else as an open issue for the HARA
- Implement fail-safe mechanisms for critical functions
- Ensure driver attention remains on the road

### Performance Targets
Use the targets stated in the requirements. Only where the requirements give no target, use the following defaults and label them as defaults:
- **App Launch**: < 3 seconds
- **API Response**: < 500ms
- **Memory Usage**: < 50MB
- **UI Responsiveness**: 60 FPS

### Security Requirements
- **Encryption**: TLS 1.2+ for network communication
- **Authentication**: Secure API key management
- **Data Protection**: Encrypt sensitive user data
- **OTA Updates**: Signed packages with rollback protection

### User Experience
- **Android Auto Compliance**: Follow platform guidelines
- **Voice Commands**: Support hands-free operation
- **Accessibility**: High contrast, large touch targets
- **Privacy**: Respect user privacy settings

## Component Design Patterns

Describe each component with the following fields, as a list or a table.

### UI Components
- **Component Name**: [ComponentName]
- **Purpose**: [Brief description]
- **Responsibilities**: [Key functions]
- **Dependencies**: [List dependencies]
- **Performance**: [Response time, memory usage]

### Business Logic Components
- **Component Name**: [ComponentName]
- **Purpose**: [Brief description]
- **Key Operations**: [Operation names and what they do, in prose]
- **Error Handling**: [Strategy]
- **Testing**: [Unit test approach]

### Data Layer Components
- **Component Name**: [ComponentName]
- **Purpose**: [Brief description]
- **Data Sources**: [APIs, databases, cache]
- **Caching Strategy**: [TTL, invalidation rules]
- **Offline Support**: [Fallback mechanisms]

## Interface Specifications

### External APIs
- **Base URL**: API endpoint, or "to be selected" if the requirements do not name a provider
- **Authentication**: Method and credentials
- **Rate Limits**: Requests per minute/hour
- **Error Codes**: Expected HTTP status codes
- **Data Format**: Field names, types and units as a table (no JSON examples)

### Vehicle Integration
- **Location Service**: GPS coordinate access
- **Connectivity Service**: Network status monitoring
- **Voice Assistant**: Command registration and responses

## Testing Strategy

### Test Coverage Targets
- **Unit Tests**: 80% code coverage
- **Integration Tests**: Critical user flows
- **Performance Tests**: Load and stress testing
- **Security Tests**: Penetration testing

### Test Types
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **System Tests**: End-to-end user scenarios
4. **Safety Tests**: Failure mode validation

## Documentation Requirements

### Code Documentation
- **Class Comments**: Purpose and usage
- **Method Comments**: Parameters and return values
- **Complex Logic**: Inline explanations

### Architecture Documentation
- **Component Diagrams**: Visual system overview
- **Sequence Diagrams**: Interaction flows
- **Data Flow Diagrams**: Information movement

## Quality Checklist

Before finalizing any technical design, verify:

- [ ] Safety classifications traceable to the requirements (or explicitly stated as not allocated)
- [ ] Performance targets taken from the requirements; any defaults labelled as defaults
- [ ] Project constraints (team, timeline, budget) copied exactly from the requirements
- [ ] Values not given in the requirements marked as proposals and listed as open issues
- [ ] No source code, build scripts or JSON payload examples
- [ ] Security measures specified
- [ ] Error handling strategies documented
- [ ] Testing approach outlined
- [ ] Implementation phases planned
- [ ] Dependencies clearly identified
- [ ] Documentation requirements met

## Common Patterns

Describe these patterns in prose when they apply. Do not write them out as code.

### Error Handling
Wrap each external call so that a network failure falls back to cached data, and any other failure is logged and shown to the user as a short, non-distracting message.

### Caching Strategy
Serve cached data while it is within its time-to-live. When it expires, fetch fresh data and update the cache. If the fetch fails, keep serving the stale data with its timestamp: stale data is better than no data.

### Performance Monitoring
Measure the duration of each critical operation and log a warning when it exceeds the target from the requirements.

## Tools and Technologies

### Recommended Stack
- **Language**: Kotlin for Android
- **Framework**: Android Auto App Library
- **Database**: Room (SQLite)
- **Networking**: OkHttp + Retrofit
- **Dependency Injection**: Hilt
- **Testing**: JUnit, Mockito, Espresso

### Development Tools
- **IDE**: Android Studio
- **Version Control**: Git
- **CI/CD**: GitHub Actions or similar
- **Static Analysis**: Detekt, Lint
- **Performance**: Profiler, Macrobenchmark

## Conclusion

These guidelines ensure technical designs are:
- **Safe**: Meet automotive safety standards
- **Faithful**: Traceable to the requirements, with assumptions clearly marked
- **Performant**: Achieve target response times
- **Secure**: Protect user data and system integrity
- **Maintainable**: Easy to understand and modify
- **Testable**: Comprehensive test coverage

Follow these patterns to create consistent, high-quality technical designs for automotive applications.
