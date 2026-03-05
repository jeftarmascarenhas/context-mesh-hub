"""MCP Tool: cm_help - Usage instructions for agents.

Provides clear instructions on how to use Context Mesh MCP tools interactively.
"""

from typing import Dict, Any

from fastmcp import FastMCP

from ..decorators import handle_mcp_errors


def register_cm_help(mcp: FastMCP):
    """Register cm_help tool with MCP server."""
    
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_help(topic: str = "overview") -> Dict[str, Any]:
        """Get help on using Context Mesh MCP tools.
        
        ⚠️ IMPORTANT: This MCP requires INTERACTIVE workflows.
        Always ask the user before creating any files.
        
        Args:
            topic: Help topic - "overview", "init", "feature", "decision", "workflow"
        
        Returns:
            Help text and instructions
        """
        
        help_content = {
            "overview": {
                "title": "Context Mesh MCP - Overview",
                "agent_rules": [
                    "⚠️ NEVER create files without asking the user first",
                    "⚠️ ALWAYS use 'questions'/'analyze' actions before 'create'/'new'",
                    "⚠️ STOP and wait for user answers before proceeding",
                    "✅ Show the user what will be created and ask for confirmation",
                ],
                "tools": {
                    "cm_init": "Initialize Context Mesh (requires user input)",
                    "cm_intent": "Manage features, decisions, bugs (requires user input for create)",
                    "cm_status": "Check project status (read-only)",
                    "cm_validate": "Validate context (read-only)",
                    "cm_build": "Build/execute plans",
                    "cm_learn": "Capture learnings",
                    "cm_agent": "Manage execution agents",
                    "cm_analyze": "Analyze existing codebases",
                },
                "workflow_principle": "Agents are operators, not authorities. MCP proposes, user approves.",
            },
            
            "init": {
                "title": "How to Initialize Context Mesh",
                "workflow": [
                    "1. Call cm_init(action='analyze') - get questions",
                    "2. STOP - Ask user each question",
                    "3. Wait for user to answer",
                    "4. Call cm_init(action='new', user_input={answers})",
                    "5. Show user the files to be created",
                    "6. Wait for user confirmation",
                    "7. Create the files",
                ],
                "example": {
                    "step1": "cm_init(action='analyze')",
                    "step2": "Ask: 'What is the name of your project?'",
                    "step3": "Ask: 'Describe what this project does'",
                    "step4": "cm_init(action='new', user_input={'project_name': 'my-api', 'description': '...', 'business_goal': '...'})",
                },
                "wrong": "cm_init(action='new', project_name='folder-name') ❌ Never auto-fill from folder",
            },
            
            "feature": {
                "title": "How to Create a Feature",
                "workflow": [
                    "1. Call cm_intent(action='questions', type='feature')",
                    "2. STOP - Ask user each question",
                    "3. Wait for user to answer",
                    "4. Call cm_intent(action='create', type='feature', content={answers})",
                    "5. Show user the file to be created",
                    "6. Wait for user confirmation",
                    "7. Create the file",
                ],
                "required_fields": ["title", "what", "why", "acceptance_criteria"],
                "example": {
                    "step1": "cm_intent(action='questions', type='feature')",
                    "step2": "Ask: 'What is the name of this feature?'",
                    "step3": "Ask: 'What does it do?', 'Why is it needed?'",
                    "step4": "cm_intent(action='create', type='feature', content={'title': '...', 'what': '...', 'why': '...', 'acceptance_criteria': [...]})",
                },
            },
            
            "decision": {
                "title": "How to Create a Decision",
                "workflow": [
                    "1. Call cm_intent(action='questions', type='decision')",
                    "2. STOP - Ask user each question",
                    "3. Wait for user to answer",
                    "4. Call cm_intent(action='create', type='decision', content={answers})",
                    "5. Show user the file to be created",
                    "6. Wait for user confirmation",
                    "7. Create the file",
                ],
                "required_fields": ["title", "context", "decision", "rationale"],
                "example": {
                    "step1": "cm_intent(action='questions', type='decision')",
                    "step2": "Ask: 'What is the decision title?'",
                    "step3": "Ask: 'What is the context?', 'What is the decision?', 'Why?'",
                    "step4": "cm_intent(action='create', type='decision', content={'title': '...', 'context': '...', 'decision': '...', 'rationale': '...'})",
                },
            },
            
            "workflow": {
                "title": "Context Mesh Workflow",
                "phases": {
                    "1_intent": "Understand WHAT and WHY before coding",
                    "2_build": "Implement following decisions and patterns",
                    "3_learn": "Capture learnings back into context",
                },
                "golden_rule": "Never assume content. Always ask the user.",
                "authority_model": "MCP proposes → User approves → Agent executes",
            },
        }
        
        if topic not in help_content:
            return {
                "error": f"Unknown topic: {topic}",
                "available_topics": list(help_content.keys()),
            }
        
        return {
            "topic": topic,
            "help": help_content[topic],
            "tip": "Remember: Always ask the user before creating anything!",
        }
    
    return cm_help
