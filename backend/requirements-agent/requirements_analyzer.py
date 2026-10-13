"""
Automotive Requirements Analyzer Agent Graph

This module implements a multi-agent system for automotive requirements analysis using Strands agents.
The system analyzes requirements documents for consistency and generates user acceptance tests if no severe issues are found.

Architecture:
- Agent 1: Requirements Consistency Analyzer
- Agent 2: User Acceptance Test Generator (conditional execution)
- Conditional edge based on consistency analysis results
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# Requirements analysis tool
@tool
def check_for_incomplete_requirements(requirements_doc_content: str) -> dict:
    """
    Runs lightweight pattern checks on a requirements document. It flags placeholder
    text (TODO, TBD, To be determined, PLACEHOLDER, XXX) and FR/NFR references that
    lack a numeric ID (e.g. a bare "FR" instead of "FR-100"). 
    
    Args:
        requirements_doc_content: The FULL TEXT CONTENT of the requirements document(s) to check.
    
    Returns:
        A dictionary with issue severity and details including:
        - issues: List of identified issues with type, description, severity, and occurrences
        - total_issues: Number of distinct issue types found (not total occurrences)
        - ready_for_development: True if no placeholder text was found
        - severity_counts: Number of issue types per severity level (high, medium, low)
    """
    issues = []
    
    # Automotive requirements analysis checks based on BRD structure
    analysis_patterns = {
        "Missing Functional Requirements IDs": {
            # Whole-word "FR" not immediately followed by "-<digits>" (skips "from", "NFR", "FR-100")
            "pattern": r"\bFR\b(?!-\d+)",
            "description": "Functional requirements should have unique identifiers (e.g., FR-100, FR-110)",
            "severity": "MEDIUM"
        },
        "Missing Non-Functional Requirements IDs": {
            # Whole-word "NFR" not immediately followed by "-<digits>" (skips "NFR-200")
            "pattern": r"\bNFR\b(?!-\d+)",
            "description": "Non-functional requirements should have unique identifiers (e.g., NFR-100, NFR-110)",
            "severity": "MEDIUM"
        },
        "Incomplete Requirements": {
            "pattern": r"\b(TODO|ToDo|TBD|To be determined|PLACEHOLDER|XXX)\b",
            "description": "Requirements contain incomplete or placeholder items",
            "severity": "HIGH"
        }
    }
    
    for issue_type, pattern_info in analysis_patterns.items():
        matches = re.findall(pattern_info["pattern"], requirements_doc_content, re.MULTILINE | re.IGNORECASE)
        if matches:
            issues.append({
                "issue_type": issue_type,
                "description": pattern_info["description"],
                "severity": pattern_info["severity"],
                "occurrences": len(matches)
            })
    
    # Count severity levels
    high_count = sum(1 for issue in issues if issue["severity"] == "HIGH")
    medium_count = sum(1 for issue in issues if issue["severity"] == "MEDIUM")
    low_count = sum(1 for issue in issues if issue["severity"] == "LOW")
    
    return {
        "issues": issues,
        "total_issues": len(issues),
        "ready_for_development": high_count == 0,
        "severity_counts": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        }
    }


# Create the model for all agents
model_id = "us.amazon.nova-2-lite-v1:0" #"us.anthropic.claude-haiku-4-5-20251001-v1:0"
model = BedrockModel(
    model_id=model_id, max_tokens=40000
)

# Create the requirements analyzer agent
requirements_analyzer_agent = Agent(
    name="requirements_analyzer",
    model=model,
    tools=[check_for_incomplete_requirements],
    system_prompt="""You are an automotive requirements analyst specializing in vehicle infotainment and safety systems. Your job is to:

1. Analyze automotive requirements documents (BRDs) for consistency, completeness, and quality
2. Evaluate requirements against automotive industry standards (ISO 26262, UNECE WP.29, Android Auto guidelines)
3. Identify issues with severity levels (LOW, MEDIUM, HIGH) based on safety and development impact
4. Assess requirements structure including:
   - Functional Requirements (FR-XXX) with acceptance criteria
   - Non-Functional Requirements (NFR-XXX) with measurable targets
   - Use cases with triggers, flows, and success criteria
   - Business drivers with success metrics
   - Safety and security considerations

IMPORTANT: Always use the check_for_incomplete_requirements tool to check if there are any missing content. Then use your expert knowledge to provide an overall assessment.

In your response, clearly state:
- **Overall Severity**: [LOW/MEDIUM/HIGH]
- **Ready for Development**: [YES/NO] 
- **Safety Assessment**: Any driver distraction or safety concerns
- **Completeness Score**: Percentage of required sections present.

Focus on automotive safety standards, driver distraction guidelines, and development readiness. Provide specific, actionable feedback for improvement."""
)

#2. Include business objective validation scenarios, 4. Create tests that are suitable for safety-critical applications
#using a minimal set of... to reduce response time.
# Create the user acceptance test generator agent
uat_generator_agent = Agent(
    name="uat_generator",
    model=model,
    system_prompt="""You are a user acceptance test generator for automotive applications. Your job is to:
1. Generate user acceptance tests based on requirements
2. Follow automotive testing standards

You receive an upstream requirements analysis report as input. Use it as context only.
Output ONLY the user acceptance test specification, starting directly with its title heading.
Do NOT restate, quote, summarize, or acknowledge the analysis report, and do NOT add any
preamble or transition text before the specification.

Generate clean, well-documented test specifications that can be easily executed by test teams."""
)

# No conditional logic - always generate UATs

# Build the multi-agent graph
def build_requirements_analyzer_graph():
    """
    Build the requirements analyzer graph with conditional workflow.
    """
    builder = GraphBuilder()
    
    # Add nodes to the graph
    builder.add_node(requirements_analyzer_agent, "requirements_analyzer")
    builder.add_node(uat_generator_agent, "uat_generator")
    
    # Add unconditional edge: always generate UATs
    builder.add_edge("requirements_analyzer", "uat_generator")
    
    # Set entry point
    builder.set_entry_point("requirements_analyzer")
    
    # Build and return the graph
    return builder.build()

# Create the graph instance
requirements_graph = build_requirements_analyzer_graph()


def extract_md(node_result) -> str:
    """
    Extract just the generated markdown document from a Strands AgentResult.

    Returning the AgentResult itself forces the runtime to stringify the whole object
    (stop_reason, metrics, traces, token usage), which bloats the response by tens of
    thousands of characters and double-escapes the markdown.
    """
    if node_result is None:
        return ""

    result = getattr(node_result, "result", node_result)
    message = getattr(result, "message", None)
    if not isinstance(message, dict):
        return str(result).strip()

    blocks = message.get("content", []) or []
    text = "\n".join(
        block["text"] for block in blocks
        if isinstance(block, dict) and isinstance(block.get("text"), str)
    )
    return text.strip() or str(result).strip()


@app.entrypoint
def automotive_requirements_analyzer(payload):
    """
    Multi-step automotive requirements analyzer using agent graph with consistency check and conditional UAT generation.
    """
    requirements_docs = payload.get("requirements_docs", "")
    if not requirements_docs:
        return {"error": "No requirements documents provided"}
    
    logger.info("Analyzing requirements documents (%d chars)", len(requirements_docs))
    
    # Create the analysis prompt
    analysis_prompt = f"""Analyze these automotive requirements documents for consistency, completeness, and quality issues:

{requirements_docs}

Please use the analyze_requirements_consistency tool to analyze the requirements and provide a comprehensive report on any issues found."""
    
    # Execute the multi-agent graph
    try:
        graph_result = requirements_graph(analysis_prompt)
        
        logger.info(
            "Graph execution completed. Nodes executed: %s/%s",
            graph_result.completed_nodes,
            graph_result.total_nodes,
        )
        logger.debug(
            "Execution order: %s",
            [node.node_id for node in graph_result.execution_order],
        )
        
        # Build the response structure
        result = {
            "execution_time_ms": graph_result.execution_time,
            "step1_requirements_analysis": {
                "analysis": extract_md(graph_result.results.get("requirements_analyzer")) or "No requirements analysis performed",
                "issues": "See analysis above for detailed issue information"
            }
        }
        
        # User acceptance tests are always generated
        if "uat_generator" in graph_result.results:
            result["step2_user_acceptance_tests"] = {
                "generated": True,
                "tests": extract_md(graph_result.results["uat_generator"])
            }
            logger.info("User acceptance tests generated successfully.")
        else:
            result["step2_user_acceptance_tests"] = {
                "generated": False,
                "reason": "User acceptance test generation failed unexpectedly."
            }
            logger.warning("User acceptance test generation failed.")
        
        # Return the final result from the graph
        return result
        
    except Exception as e:
        logger.exception("Graph execution failed")
        return {
            "error": f"Graph execution failed: {str(e)}",
            "step1_requirements_analysis": {"analysis": "Analysis failed", "issues": []},
            "step2_user_acceptance_tests": {"generated": False, "reason": "Graph execution failed"}
        }

if __name__ == "__main__":
    app.run()