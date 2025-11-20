# Automotive Technical Design Generator

This directory contains a comprehensive automotive technical design generator implemented using Strands Agents framework and deployed on Amazon Bedrock AgentCore Runtime. The agent generates technical design documents from business requirements (BRD), software requirements specification(SRS), and other supporting documents.

## Overview

The Technical Design Generator transforms validated requirements documents into comprehensive technical design documents for automotive software development. 

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│  AgentCore       │───▶│  Design Agent   │
│ (design-server) │    │  Runtime         │    │  (Strands)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  AgentCore       │    │  S3 Guidelines  │
                       │  Gateway         │    │  (via Lambda)   │
                       └──────────────────┘    └─────────────────┘
```

- **Agent**: Design generation
- **Framework**: Strands Agents with AgentCore Gateway integration
- **Authentication**: Amazon Cognito with JWT tokens
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Models**: Claude 4.5 Haiku
- **Guidelines**: S3-stored design guidelines accessed via AgentCore Gateway

## Components

### 1. Design Generator Agent (`design_generator.py`)
- **Primary Agent**: Generates comprehensive technical design documents
- **Model**: Claude 3.5 Sonnet for high-quality design generation
- **Tools**: AgentCore Gateway tools for accessing design guidelines
- **Output**: Complete technical design with architecture, safety, and implementation sections

### 2. AgentCore Gateway Integration
- **S3 Guidelines**: Design guidelines stored in S3 bucket
- **Lambda Functions**: Retrieve guidelines by type and category
- **JWT Authentication**: Secure access using Cognito tokens
- **MCP Protocol**: Standard Model Context Protocol interface

### 3. Infrastructure (CloudFormation)
- **S3 Bucket**: Stores design guidelines and templates
- **Lambda Functions**: Guidelines retrieval and processing
- **IAM Roles**: Proper permissions for AgentCore and Gateway
- **Cognito Integration**: JWT-based authentication

## Quick Start

### Prerequisites
- Python 3.13+
- AWS CLI configured
- Amazon Bedrock access
- AgentCore Runtime permissions

### 1. Deploy Infrastructure
Run notebook.
