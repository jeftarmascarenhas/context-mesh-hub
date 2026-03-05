"""MCP Tool: cm_intent - Intent management.

Tool 2 of 8: CRUD for features, decisions, bugs, and project intent.

IMPORTANT: This tool is INTERACTIVE for create actions.
The agent MUST ask the user questions and wait for answers before creating artifacts.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from fastmcp import FastMCP

from ...domain.services.intent_service import IntentService
from ...shared.errors import ArtifactNotFoundError, ValidationError
from ..decorators import handle_mcp_errors


# Questions for each artifact type
_ARTIFACT_QUESTIONS = {
    "feature": [
        {
            "id": "title",
            "question": "What is the name/title of this feature?",
            "required": True,
            "example": "User Authentication, API Rate Limiting, Dark Mode"
        },
        {
            "id": "what",
            "question": "What does this feature do? (describe the functionality)",
            "required": True,
            "example": "Allows users to log in with email/password and receive a JWT token"
        },
        {
            "id": "why",
            "question": "Why is this feature needed? (business value)",
            "required": True,
            "example": "Users need secure access to their accounts across devices"
        },
        {
            "id": "acceptance_criteria",
            "question": "What are the acceptance criteria? (list items separated by semicolons)",
            "required": True,
            "example": "User can login with email/password; JWT is returned on success; Invalid credentials show error"
        },
    ],
    "decision": [
        {
            "id": "title",
            "question": "What is the title of this decision?",
            "required": True,
            "example": "Use PostgreSQL for primary database"
        },
        {
            "id": "context",
            "question": "What is the context/problem that requires this decision?",
            "required": True,
            "example": "We need a database that supports complex queries and ACID transactions"
        },
        {
            "id": "decision",
            "question": "What is the decision?",
            "required": True,
            "example": "We will use PostgreSQL 15 as the primary database"
        },
        {
            "id": "rationale",
            "question": "Why this decision? What is the rationale?",
            "required": True,
            "example": "PostgreSQL provides JSONB support, excellent performance, and is well-supported"
        },
        {
            "id": "alternatives",
            "question": "What alternatives were considered? (optional, separate by semicolons)",
            "required": False,
            "example": "MySQL - less JSONB support; MongoDB - no ACID; SQLite - not scalable"
        },
    ],
    "bug": [
        {
            "id": "title",
            "question": "What is the bug title?",
            "required": True,
            "example": "Login fails with special characters in password"
        },
        {
            "id": "description",
            "question": "Describe the bug",
            "required": True,
            "example": "When a user's password contains special characters like @#$, login fails"
        },
        {
            "id": "expected",
            "question": "What should happen (expected behavior)?",
            "required": True,
            "example": "User should be able to login regardless of special characters"
        },
        {
            "id": "actual",
            "question": "What actually happens?",
            "required": True,
            "example": "Server returns 500 error and user cannot login"
        },
        {
            "id": "impact",
            "question": "What is the impact?",
            "required": False,
            "example": "~15% of users cannot login, causing support tickets"
        },
    ],
}


def register_cm_intent(
    mcp: FastMCP,
    intent_service: IntentService,
):
    """Register cm_intent tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        intent_service: IntentService instance
    """
    
    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_intent(
        action: str,
        type: str,
        name: Optional[str] = None,
        content: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Manage context intents: features, decisions, and bugs.
        
        ⚠️ INTERACTIVE WORKFLOW for create - Agent must ask user questions first!
        
        CORRECT WORKFLOW for creating artifacts:
        1. Call cm_intent(action="questions", type="feature") to get questions
        2. STOP and ask user each question
        3. Wait for user answers
        4. Call cm_intent(action="create", type="feature", content={answers})
        
        Args:
            action: Action to perform:
                - "questions": Get questions to ask user (START HERE for create)
                - "create": Create artifact (requires content with user answers)
                - "update", "get", "list", "delete", "spec": Other operations
            type: Intent type - "feature", "decision", "bug", "project"
            name: Identifier for get/update/delete
            content: User answers for create/update (REQUIRED, from user)
        
        Examples:
            # Step 1: Get questions for feature
            cm_intent(action="questions", type="feature")
            
            # Step 2: After asking user
            cm_intent(action="create", type="feature", content={
                "title": "User Authentication",
                "what": "JWT-based auth system",
                "why": "Secure user access",
                "acceptance_criteria": ["User can login", "JWT is returned"]
            })
        """
        valid_actions = ["questions", "create", "update", "get", "list", "delete", "spec"]
        valid_types = ["feature", "decision", "bug", "project", "pattern", "anti-pattern"]
        
        if action not in valid_actions:
            return {"error": f"Invalid action: {action}", "valid_actions": valid_actions}
        if type not in valid_types:
            return {"error": f"Invalid type: {type}", "valid_types": valid_types}
        
        # ====================================================================
        # ACTION: QUESTIONS - Return questions for the user
        # ====================================================================
        if action == "questions":
            if type not in _ARTIFACT_QUESTIONS:
                return {
                    "error": f"No questions defined for type: {type}",
                    "tip": f"For {type}, use action='get' or action='list' instead",
                }
            
            return {
                "status": "questions_required",
                "type": type,
                "message": f"Before creating a {type}, I need some information.",
                "agent_instruction": f"⚠️ STOP. Ask the user EACH question below to create a {type}. Do NOT proceed until you have answers.",
                "questions": _ARTIFACT_QUESTIONS[type],
                "next_step": f"After getting answers, call: cm_intent(action='create', type='{type}', content={{...}})",
            }
        
        # ====================================================================
        # ACTION: SPEC - Get artifact specification
        # ====================================================================
        if action == "spec":
            specs = {
                "feature": {
                    "naming_convention": {
                        "format": "F00X-description.md",
                        "rules": [
                            "Must start with F followed by 3-4 digits",
                            "Use lowercase with hyphens for description",
                            "Sequential numbering (don't skip numbers)"
                        ],
                        "examples": ["F001-user-authentication.md", "F002-api-gateway.md"]
                    },
                    "required_sections": ["What", "Why", "Acceptance Criteria", "Status"],
                    "recommended_sections": ["How", "Related"],
                    "optional_sections": ["Constraints"],
                    "structure": "# Feature: [Title]\n\n## What\n\n[Description]\n\n## Why\n\n[Justification]\n\n## How\n\n[Implementation approach]\n\n## Acceptance Criteria\n\n- [ ] Criterion 1\n\n## Constraints\n\n[Constraints]\n\n## Related\n\n- **Decision**: [DXX - Name](../decisions/DXX-*.md)\n\n## Status\n\n- **Created**: YYYY-MM-DD\n- **Status**: Active",
                    "validation_rules": [
                        "All required sections must be present",
                        "Acceptance Criteria must use checkboxes",
                        "Status must include Created date and current status",
                        "Related links must use relative paths"
                    ]
                },
                "decision": {
                    "naming_convention": {
                        "format": "D00X-description.md",
                        "rules": [
                            "Must start with D followed by 3-4 digits",
                            "Use lowercase with hyphens for description",
                            "Sequential numbering (don't skip numbers)"
                        ],
                        "examples": ["D001-tech-stack.md", "D002-auth-approach.md"]
                    },
                    "required_sections": ["Context", "Decision", "Rationale", "Status"],
                    "recommended_sections": ["Alternatives Considered", "Consequences", "Related"],
                    "optional_sections": ["Outcomes"],
                    "structure": "# Decision: [Title]\n\n## Context\n\n[Problem statement]\n\n## Decision\n\n[Decision made]\n\n## Rationale\n\n[Why this decision]\n\n## Alternatives Considered\n\n[Other options]\n\n## Consequences\n\n### Positive\n- Benefit 1\n\n### Trade-offs\n- Trade-off 1\n\n## Outcomes\n\n[Added after implementation]\n\n## Related\n\n- [Feature: FXX](../intent/FXX-*.md)\n\n## Status\n\n- **Created**: YYYY-MM-DD\n- **Status**: Proposed | Accepted | Superseded",
                    "validation_rules": [
                        "All required sections must be present",
                        "Status must include Created date and current status",
                        "Consequences should have Positive and Trade-offs subsections",
                        "Related links must use relative paths"
                    ]
                },
                "pattern": {
                    "naming_convention": {
                        "format": "descriptive-name.md",
                        "rules": [
                            "Use lowercase with hyphens",
                            "Descriptive, not numbered",
                            "Should be reusable across projects"
                        ],
                        "examples": ["phased-refactoring-with-di.md", "event-sourcing-pattern.md"]
                    },
                    "required_sections": ["Context", "The Pattern", "Evidence", "Status"],
                    "recommended_sections": ["Why It Works", "When to Use", "When NOT to Use", "Implementation Guide"],
                    "optional_sections": ["Anti-Patterns to Avoid", "Related"],
                    "validation_rules": [
                        "Evidence section must have real-world examples",
                        "Status must include Confidence and Impact levels"
                    ]
                },
                "anti-pattern": {
                    "naming_convention": {
                        "format": "descriptive-problem-name.md",
                        "rules": [
                            "Use lowercase with hyphens",
                            "Descriptive, not numbered",
                            "Should clearly identify the problem"
                        ],
                        "examples": ["python-relative-imports-pitfall.md", "god-object-antipattern.md"]
                    },
                    "required_sections": ["Context", "The Problem", "Evidence", "Recommendation", "Status"],
                    "recommended_sections": ["Why It Happens", "Related"],
                    "optional_sections": [],
                    "validation_rules": [
                        "Evidence section must have real examples",
                        "Recommendation must show correct approach"
                    ]
                },
                "project": {
                    "naming_convention": {
                        "format": "project-intent.md",
                        "rules": ["Fixed name: project-intent.md"],
                        "examples": ["project-intent.md"]
                    },
                    "required_sections": ["What", "Why", "Scope", "Acceptance Criteria", "Status"],
                    "recommended_sections": ["Constraints", "Related"],
                    "optional_sections": [],
                    "validation_rules": [
                        "Must exist in context/intent/project-intent.md",
                        "Scope must have Core Capabilities and Out of Scope subsections"
                    ]
                }
            }
            
            if type in specs:
                return {
                    "action": "spec",
                    "type": type,
                    "specification": specs[type],
                    "full_spec_location": "context/knowledge/ARTIFACT_SPECS.md",
                    "tip": "Always consult ARTIFACT_SPECS.md before creating artifacts"
                }
            else:
                return {"error": f"No specification available for type: {type}"}
        
        # ====================================================================
        # ACTION: GET
        # ====================================================================
        if action == "get":
            if type == "project":
                result = intent_service.get_project_intent()
                return {
                    "action": "get",
                    "type": type,
                    "path": result["path"],
                    "content": result["content"],
                }
            
            if not name:
                return {"error": "Name required for get action", "type": type}
            
            if type == "feature":
                result = intent_service.get_feature(name)
                return {
                    "action": "get",
                    "type": type,
                    "name": result["name"],
                    "path": result["path"],
                    "content": result["content"],
                    "status": result["status"],
                    "title": result["title"],
                }
            
            elif type == "decision":
                result = intent_service.get_decision(name)
                return {
                    "action": "get",
                    "type": type,
                    "name": result["name"],
                    "path": result["path"],
                    "content": result["content"],
                    "status": result["status"],
                    "title": result["title"],
                }
            
            elif type == "bug":
                result = intent_service.get_bug(name)
                return {
                    "action": "get",
                    "type": type,
                    "name": result["name"],
                    "path": result["path"],
                    "content": result["content"],
                }
        
        # ====================================================================
        # ACTION: LIST
        # ====================================================================
        elif action == "list":
            if type == "feature":
                features = intent_service.list_features()
                return {
                    "action": "list",
                    "type": type,
                    "total": len(features),
                    "items": features,
                }
            
            elif type == "decision":
                decisions = intent_service.list_decisions()
                return {
                    "action": "list",
                    "type": type,
                    "total": len(decisions),
                    "items": decisions,
                }
            
            elif type == "bug":
                bugs = intent_service.list_bugs()
                return {
                    "action": "list",
                    "type": type,
                    "total": len(bugs),
                    "items": bugs,
                }
            
            elif type == "project":
                try:
                    result = intent_service.get_project_intent()
                    return {
                        "action": "list",
                        "type": type,
                        "exists": True,
                        "path": result["path"],
                    }
                except ArtifactNotFoundError:
                    return {
                        "action": "list",
                        "type": type,
                        "exists": False,
                        "path": None,
                    }
        
        # ====================================================================
        # ACTION: CREATE
        # ====================================================================
        elif action == "create":
            # Validate content is provided
            if not content:
                return {
                    "error": "Missing content parameter",
                    "status": "input_required",
                    "agent_instruction": f"⚠️ STOP. You must first ask the user questions. Call cm_intent(action='questions', type='{type}') to get the questions.",
                    "workflow": [
                        f"1. cm_intent(action='questions', type='{type}') - get questions",
                        "2. Ask user each question",
                        f"3. cm_intent(action='create', type='{type}', content={{answers}})"
                    ],
                }
            
            # Validate required fields based on type
            if type in _ARTIFACT_QUESTIONS:
                required = [q["id"] for q in _ARTIFACT_QUESTIONS[type] if q["required"]]
                missing = [f for f in required if not content.get(f)]
                if missing:
                    return {
                        "error": f"Missing required fields: {missing}",
                        "status": "incomplete_input",
                        "agent_instruction": f"⚠️ STOP. Ask the user for: {', '.join(missing)}",
                        "required_fields": required,
                        "provided_fields": list(content.keys()),
                        "questions": [q for q in _ARTIFACT_QUESTIONS[type] if q["id"] in missing],
                    }
            
            if type == "feature":
                # Parse acceptance_criteria if string with semicolons
                ac = content.get("acceptance_criteria", [])
                if isinstance(ac, str):
                    ac = [c.strip() for c in ac.split(";") if c.strip()]
                
                result = intent_service.create_feature(
                    title=content.get("title", "Untitled Feature"),
                    what=content.get("what", "_Describe what this feature does_"),
                    why=content.get("why", "_Explain why this feature is needed_"),
                    acceptance_criteria=ac if ac else ["Criteria 1", "Criteria 2"],
                    related_decisions=content.get("related_decisions", []),
                )
                return {
                    "action": "create",
                    "type": type,
                    "status": "ready_to_create",
                    "id": result["id"],
                    "file_path": result["file_path"],
                    "file_content": result["file_content"],
                    "agent_instruction": "Show the user what will be created and ask for confirmation before creating the file.",
                    "next_step": "After user approval, create this file. Then use cm_intent(action='questions', type='decision') to add technical approach.",
                }
            
            elif type == "decision":
                # Parse alternatives if string with semicolons
                alts = content.get("alternatives", [])
                if isinstance(alts, str):
                    alts = [a.strip() for a in alts.split(";") if a.strip()]
                
                result = intent_service.create_decision(
                    title=content.get("title", "Untitled Decision"),
                    context=content.get("context", "_Describe the situation and constraints_"),
                    decision=content.get("decision", "_State the decision made_"),
                    rationale=content.get("rationale", "_Explain why this decision was made_"),
                    alternatives=alts,
                    consequences=content.get("consequences", {"positive": ["_Benefits_"], "tradeoffs": ["_Trade-offs_"]}),
                    related_features=content.get("related_features", []),
                    related_decisions=content.get("related_decisions", []),
                )
                return {
                    "action": "create",
                    "type": type,
                    "status": "ready_to_create",
                    "id": result["id"],
                    "file_path": result["file_path"],
                    "file_content": result["file_content"],
                    "agent_instruction": "Show the user what will be created and ask for confirmation before creating the file.",
                }
            
            elif type == "bug":
                result = intent_service.create_bug(
                    title=content.get("title", "Untitled Bug"),
                    description=content.get("description", "_Describe the bug_"),
                    expected=content.get("expected", "_What should happen_"),
                    actual=content.get("actual", "_What actually happens_"),
                    impact=content.get("impact", "_Who/what is affected_"),
                    related_feature=content.get("related_feature", "_Related feature if any_"),
                )
                return {
                    "action": "create",
                    "type": type,
                    "status": "ready_to_create",
                    "file_path": result["file_path"],
                    "file_content": result["file_content"],
                    "agent_instruction": "Show the user what will be created and ask for confirmation before creating the file.",
                }
        
        # ====================================================================
        # ACTION: UPDATE
        # ====================================================================
        elif action == "update":
            if not name:
                return {"error": "Name required for update action"}
            if not content:
                return {"error": "Content required for update action"}
            
            if type == "feature":
                result = intent_service.update_feature(name, content)
                return {
                    "action": "update",
                    "type": type,
                    "name": result["name"],
                    "file_path": result["path"],
                    "updated_content": result["updated_content"],
                    "changes_applied": list(content.keys()),
                }
            
            elif type == "decision":
                result = intent_service.update_decision(name, content)
                return {
                    "action": "update",
                    "type": type,
                    "name": result["name"],
                    "file_path": result["path"],
                    "updated_content": result["updated_content"],
                    "changes_applied": list(content.keys()),
                }
        
        # ====================================================================
        # ACTION: DELETE
        # ====================================================================
        elif action == "delete":
            if not name:
                return {"error": "Name required for delete action"}
            
            # Get artifact to confirm it exists and get path
            if type == "feature":
                result = intent_service.get_feature(name)
            elif type == "decision":
                result = intent_service.get_decision(name)
            elif type == "bug":
                result = intent_service.get_bug(name)
            else:
                return {"error": f"Delete not supported for type: {type}"}
            
            return {
                "action": "delete",
                "type": type,
                "name": result["name"],
                "file_path": result["path"],
                "warning": "This will delete the file. Use 'git rm' to preserve history.",
                "confirm_command": f"git rm {result['path']}",
            }
