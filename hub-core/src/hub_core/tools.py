"""MCP tool definitions for Hub Core."""

from typing import Optional
from pathlib import Path

from fastmcp import FastMCP

from .loader import ContextLoader
from .validator import ContextValidator
from .bundler import ContextBundler
from .build_protocol import BuildProtocol
from .brownfield import RepositoryScanner, SliceGenerator, ContextExtractor
from .learn_sync import LearnSync
from .prompt_resolver import PromptResolver
from .prompt_pack_manager import PromptPackManager


def create_tools(mcp: FastMCP, repo_root: Optional[Path] = None):
    """Register MCP tools with the server.
    
    Args:
        mcp: FastMCP server instance.
        repo_root: Optional repository root path. Auto-detects if None.
    """
    loader = ContextLoader(repo_root)
    validator = ContextValidator(loader)
    bundler = ContextBundler(loader)
    build_protocol = BuildProtocol(loader, bundler)
    scanner = RepositoryScanner(repo_root)
    slice_generator = SliceGenerator(scanner)
    context_extractor = ContextExtractor(scanner)
    learn_sync = LearnSync(loader)
    prompt_resolver = PromptResolver(repo_root or Path.cwd())
    pack_manager = PromptPackManager(repo_root or Path.cwd())
    
    # Load context index on startup
    try:
        loader.load()
    except Exception as e:
        # Index will be loaded lazily on first tool call if needed
        pass
    
    @mcp.tool()
    def context_read(
        artifact_type: str,
        name: str
    ) -> dict:
        """Read a context artifact.
        
        Args:
            artifact_type: Type of artifact: "project_intent", "feature_intent", "decision", "knowledge", "agent", "changelog".
            name: Identifier:
                - For feature_intent: feature name (e.g., "hub-core")
                - For decision: decision number (e.g., "001")
                - For knowledge: pattern/anti-pattern name
                - For agent: agent name
                - For project_intent or changelog: ignored
        
        Returns:
            Dictionary with artifact content and metadata.
        """
        try:
            index = loader.index
            
            if artifact_type == "project_intent":
                artifact = index.get("project_intent")
                if not artifact:
                    return {
                        "error": "Project intent not found",
                        "artifact_type": artifact_type,
                    }
                return {
                    "artifact_type": artifact_type,
                    "path": artifact["path"],
                    "content": artifact["content"],
                }
            
            elif artifact_type == "feature_intent":
                artifact = index["feature_intents"].get(name)
                if not artifact:
                    return {
                        "error": f"Feature intent not found: {name}",
                        "artifact_type": artifact_type,
                        "name": name,
                    }
                return {
                    "artifact_type": artifact_type,
                    "name": name,
                    "path": artifact["path"],
                    "content": artifact["content"],
                }
            
            elif artifact_type == "decision":
                artifact = index["decisions"].get(name)
                if not artifact:
                    return {
                        "error": f"Decision not found: {name}",
                        "artifact_type": artifact_type,
                        "number": name,
                    }
                return {
                    "artifact_type": artifact_type,
                    "number": name,
                    "path": artifact["path"],
                    "content": artifact["content"],
                }
            
            elif artifact_type == "knowledge":
                # Name format: "patterns/pattern-name" or "anti-patterns/pattern-name"
                parts = name.split("/", 1)
                if len(parts) != 2:
                    return {
                        "error": f"Invalid knowledge name format. Expected 'patterns/name' or 'anti-patterns/name', got: {name}",
                        "artifact_type": artifact_type,
                    }
                category, pattern_name = parts
                if category not in ["patterns", "anti-patterns"]:
                    return {
                        "error": f"Invalid knowledge category: {category}. Must be 'patterns' or 'anti-patterns'",
                        "artifact_type": artifact_type,
                    }
                artifact = index["knowledge"][category].get(pattern_name)
                if not artifact:
                    return {
                        "error": f"Knowledge artifact not found: {name}",
                        "artifact_type": artifact_type,
                        "name": name,
                    }
                return {
                    "artifact_type": artifact_type,
                    "category": category,
                    "name": pattern_name,
                    "path": artifact["path"],
                    "content": artifact["content"],
                }
            
            elif artifact_type == "agent":
                artifact = index["agents"].get(name)
                if not artifact:
                    return {
                        "error": f"Agent not found: {name}",
                        "artifact_type": artifact_type,
                        "name": name,
                    }
                return {
                    "artifact_type": artifact_type,
                    "name": name,
                    "path": artifact["path"],
                    "content": artifact["content"],
                }
            
            elif artifact_type == "changelog":
                artifact = index.get("changelog")
                if not artifact:
                    return {
                        "error": "Changelog not found",
                        "artifact_type": artifact_type,
                    }
                return {
                    "artifact_type": artifact_type,
                    "path": artifact["path"],
                    "content": artifact["content"],
                }
            
            else:
                return {
                    "error": f"Unknown artifact type: {artifact_type}",
                    "artifact_type": artifact_type,
                }
        
        except Exception as e:
            return {
                "error": f"Error reading artifact: {str(e)}",
                "artifact_type": artifact_type,
                "name": name,
            }
    
    @mcp.tool()
    def context_validate() -> dict:
        """Validate Context Mesh repository structure and content.
        
        Returns:
            Dictionary with validation results (errors, warnings, info).
        """
        try:
            result = validator.validate()
            
            return {
                "valid": result.valid,
                "errors": [
                    {
                        "message": issue.message,
                        "artifact": issue.artifact,
                    }
                    for issue in result.errors
                ],
                "warnings": [
                    {
                        "message": issue.message,
                        "artifact": issue.artifact,
                    }
                    for issue in result.warnings
                ],
                "info": [
                    {
                        "message": issue.message,
                        "artifact": issue.artifact,
                    }
                    for issue in result.info
                ],
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}",
                "errors": [],
                "warnings": [],
                "info": [],
            }
    
    @mcp.tool()
    def context_bundle(
        bundle_type: str,
        identifier: str
    ) -> dict:
        """Generate a context bundle.
        
        Args:
            bundle_type: Type of bundle: "project", "feature", or "decision".
            identifier:
                - For "project": ignored (use "project")
                - For "feature": feature name (e.g., "hub-core")
                - For "decision": decision number (e.g., "001")
        
        Returns:
            Dictionary with bundle content and metadata.
        """
        try:
            if bundle_type == "project":
                bundle = bundler.bundle_project()
            elif bundle_type == "feature":
                bundle = bundler.bundle_feature(identifier)
            elif bundle_type == "decision":
                bundle = bundler.bundle_decision(identifier)
            else:
                return {
                    "error": f"Unknown bundle type: {bundle_type}. Must be 'project', 'feature', or 'decision'",
                    "bundle_type": bundle_type,
                }
            
            return bundle
        
        except ValueError as e:
            return {
                "error": str(e),
                "bundle_type": bundle_type,
                "identifier": identifier,
            }
        except Exception as e:
            return {
                "error": f"Error generating bundle: {str(e)}",
                "bundle_type": bundle_type,
                "identifier": identifier,
            }
    
    @mcp.tool()
    def hub_health() -> dict:
        """Health check for Hub Core MCP server.
        
        Returns:
            Dictionary with server status, repository root, and context index status.
        """
        try:
            index = loader.index
            repo_root_str = str(loader.repo_root)
            
            # Count artifacts
            stats = {
                "project_intent": 1 if index.get("project_intent") else 0,
                "feature_intents": len(index["feature_intents"]),
                "decisions": len(index["decisions"]),
                "knowledge_patterns": len(index["knowledge"]["patterns"]),
                "knowledge_anti_patterns": len(index["knowledge"]["anti-patterns"]),
                "agents": len(index["agents"]),
                "changelog": 1 if index.get("changelog") else 0,
            }
            
            return {
                "status": "healthy",
                "repo_root": repo_root_str,
                "context_dir": str(loader.context_dir),
                "index_loaded": loader._loaded,
                "artifact_counts": stats,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    @mcp.tool()
    def build_plan(feature_name: str) -> dict:
        """Generate a build plan for a feature.
        
        Args:
            feature_name: Name of the feature (e.g., "hub-core").
        
        Returns:
            Dictionary with build plan details.
        """
        try:
            plan = build_protocol.create_plan(feature_name)
            
            return {
                "plan_id": plan.plan_id,
                "feature_name": plan.feature_name,
                "feature_path": plan.feature_path,
                "created_at": plan.created_at,
                "implementation_steps": [
                    {
                        "step_number": step.step_number,
                        "description": step.description,
                        "target_files": step.target_files,
                        "operations": step.operations,
                        "constraints": step.constraints,
                        "validation_checks": step.validation_checks,
                    }
                    for step in plan.implementation_steps
                ],
                "target_files": plan.target_files,
                "constraints": plan.constraints,
                "non_goals": plan.non_goals,
                "risks": plan.risks,
                "assumptions": plan.assumptions,
                "related_decisions": plan.related_decisions,
                "acceptance_criteria": plan.acceptance_criteria,
            }
        except ValueError as e:
            return {
                "error": str(e),
                "feature_name": feature_name,
            }
        except Exception as e:
            return {
                "error": f"Error creating plan: {str(e)}",
                "feature_name": feature_name,
            }
    
    @mcp.tool()
    def build_approve(
        plan_id: str,
        action: str,
        scope: Optional[list] = None,
        feedback: Optional[str] = None
    ) -> dict:
        """Approve or reject a build plan.
        
        Args:
            plan_id: Plan ID to approve/reject.
            action: "approve" or "reject".
            scope: Optional list of step numbers for partial approval.
            feedback: Optional feedback message.
        
        Returns:
            Dictionary with approval status.
        """
        try:
            approval = build_protocol.approve_plan(
                plan_id=plan_id,
                action=action,
                scope=scope,
                feedback=feedback
            )
            
            return {
                "plan_id": approval.plan_id,
                "status": approval.status.value,
                "approved_at": approval.approved_at,
                "approved_scope": approval.approved_scope,
                "rejection_feedback": approval.rejection_feedback,
                "notes": approval.notes,
            }
        except ValueError as e:
            return {
                "error": str(e),
                "plan_id": plan_id,
            }
        except Exception as e:
            return {
                "error": f"Error processing approval: {str(e)}",
                "plan_id": plan_id,
            }
    
    @mcp.tool()
    def build_execute(
        plan_id: str,
        mode: str = "instruction"
    ) -> dict:
        """Generate execution instructions from an approved plan.
        
        Args:
            plan_id: Plan ID to generate instructions for.
            mode: Execution mode ("instruction" or "assisted").
        
        Returns:
            Dictionary with execution instructions.
        """
        try:
            instructions = build_protocol.generate_instructions(plan_id, mode)
            
            return {
                "plan_id": plan_id,
                "mode": mode,
                "instructions": [
                    {
                        "instruction_id": inst.instruction_id,
                        "step_number": inst.step_number,
                        "operation": inst.operation,
                        "target_file": inst.target_file,
                        "description": inst.description,
                        "validation_check": inst.validation_check,
                        "constraints": inst.constraints,
                    }
                    for inst in instructions
                ],
                "instruction_count": len(instructions),
            }
        except ValueError as e:
            return {
                "error": str(e),
                "plan_id": plan_id,
            }
        except Exception as e:
            return {
                "error": f"Error generating instructions: {str(e)}",
                "plan_id": plan_id,
            }
    
    @mcp.tool()
    def brownfield_scan(path: Optional[str] = None) -> dict:
        """Scan repository structure for brownfield analysis.
        
        Args:
            path: Optional path to scan (defaults to repository root).
        
        Returns:
            Dictionary with structural analysis results.
        """
        try:
            scan_path = Path(path) if path else scanner.repo_root
            temp_scanner = RepositoryScanner(scan_path)
            analysis = temp_scanner.scan()
            
            return {
                "repo_root": analysis.repo_root,
                "languages": sorted(list(analysis.languages)),
                "frameworks": sorted(list(analysis.frameworks)),
                "entry_points": analysis.entry_points,
                "build_tools": analysis.build_tools,
                "test_presence": analysis.test_presence,
                "file_count": analysis.file_count,
                "total_size": analysis.total_size,
                "directory_structure": {
                    k: {
                        "files": v["files"][:10],  # Limit file listing
                        "subdirs": v["subdirs"][:10],  # Limit subdir listing
                    }
                    for k, v in list(analysis.directory_structure.items())[:20]  # Limit to 20 dirs
                },
            }
        except Exception as e:
            return {
                "error": f"Error scanning repository: {str(e)}",
                "path": path,
            }
    
    @mcp.tool()
    def brownfield_slice(strategy: str = "directory") -> dict:
        """Generate repository slices for brownfield analysis.
        
        Args:
            strategy: Slice strategy ("directory", "module", "language").
        
        Returns:
            Dictionary with slice definitions.
        """
        try:
            slices = slice_generator.generate_slices(strategy)
            
            return {
                "strategy": strategy,
                "slice_count": len(slices),
                "slices": [
                    {
                        "slice_id": slice_def.slice_id,
                        "name": slice_def.name,
                        "paths": slice_def.paths,
                        "languages": sorted(list(slice_def.languages)),
                        "file_count": slice_def.file_count,
                        "dependencies": slice_def.dependencies,
                    }
                    for slice_def in slices
                ],
            }
        except ValueError as e:
            return {
                "error": str(e),
                "strategy": strategy,
            }
        except Exception as e:
            return {
                "error": f"Error generating slices: {str(e)}",
                "strategy": strategy,
            }
    
    @mcp.tool()
    def brownfield_extract(slice_id: Optional[str] = None, path: Optional[str] = None) -> dict:
        """Extract proposed context artifacts from a repository slice.
        
        Args:
            slice_id: Slice ID to extract from (from brownfield_slice).
            path: Alternative: path to extract from (creates temporary slice).
        
        Returns:
            Dictionary with proposed context artifacts.
        """
        try:
            if slice_id:
                # Find slice by ID
                slices = slice_generator.generate_slices()
                slice_def = next((s for s in slices if s.slice_id == slice_id), None)
                if not slice_def:
                    return {
                        "error": f"Slice not found: {slice_id}",
                        "slice_id": slice_id,
                    }
            elif path:
                # Create temporary slice from path
                from .brownfield import SliceDefinition
                slice_def = SliceDefinition(
                    slice_id="temp-slice",
                    name=Path(path).name,
                    paths=[path],
                    languages=set(),
                    file_count=0,
                )
            else:
                return {
                    "error": "Either slice_id or path must be provided",
                }
            
            artifacts = context_extractor.extract_from_slice(slice_def)
            
            return {
                "slice_id": slice_def.slice_id,
                "slice_name": slice_def.name,
                "artifact_count": len(artifacts),
                "artifacts": [
                    {
                        "artifact_type": artifact.artifact_type,
                        "title": artifact.title,
                        "content": artifact.content,
                        "confidence": artifact.confidence.value,
                        "evidence": [
                            {
                                "file_path": ev.file_path,
                                "line_range": ev.line_range,
                                "description": ev.description,
                            }
                            for ev in artifact.evidence
                        ],
                        "open_questions": artifact.open_questions,
                    }
                    for artifact in artifacts
                ],
            }
        except Exception as e:
            return {
                "error": f"Error extracting context: {str(e)}",
                "slice_id": slice_id,
                "path": path,
            }
    
    @mcp.tool()
    def brownfield_report(slice_filter: Optional[str] = None) -> dict:
        """Generate comprehensive brownfield analysis report.
        
        Args:
            slice_filter: Optional slice ID to filter report (defaults to all slices).
        
        Returns:
            Dictionary with comprehensive brownfield report.
        """
        try:
            # Scan repository
            analysis = scanner.scan()
            
            # Generate slices
            slices = slice_generator.generate_slices()
            
            # Extract from slices
            all_artifacts = []
            for slice_def in slices:
                if slice_filter and slice_def.slice_id != slice_filter:
                    continue
                artifacts = context_extractor.extract_from_slice(slice_def)
                all_artifacts.extend(artifacts)
            
            # Categorize artifacts
            by_type: dict = {}
            for artifact in all_artifacts:
                if artifact.artifact_type not in by_type:
                    by_type[artifact.artifact_type] = []
                by_type[artifact.artifact_type].append({
                    "title": artifact.title,
                    "confidence": artifact.confidence.value,
                    "evidence_count": len(artifact.evidence),
                })
            
            return {
                "structural_analysis": {
                    "languages": sorted(list(analysis.languages)),
                    "frameworks": sorted(list(analysis.frameworks)),
                    "entry_points": analysis.entry_points,
                    "build_tools": analysis.build_tools,
                    "test_presence": analysis.test_presence,
                    "file_count": analysis.file_count,
                },
                "slices": {
                    "count": len(slices),
                    "slice_ids": [s.slice_id for s in slices],
                },
                "extracted_artifacts": {
                    "total": len(all_artifacts),
                    "by_type": {
                        k: len(v) for k, v in by_type.items()
                    },
                    "artifacts": by_type,
                },
                "summary": {
                    "repository_size": analysis.file_count,
                    "languages_detected": len(analysis.languages),
                    "slices_analyzed": len(slices),
                    "artifacts_proposed": len(all_artifacts),
                },
            }
        except Exception as e:
            return {
                "error": f"Error generating report: {str(e)}",
            }
    
    @mcp.tool()
    def learn_sync_initiate(
        feature_name: str,
        changed_files: Optional[list] = None,
        test_results: Optional[str] = None,
        execution_transcript: Optional[str] = None,
        user_feedback: Optional[str] = None
    ) -> dict:
        """Initiate Learn Sync for a feature after execution.
        
        Args:
            feature_name: Name of the feature (e.g., "hub-core").
            changed_files: Optional list of changed file paths.
            test_results: Optional test results summary.
            execution_transcript: Optional execution transcript.
            user_feedback: Optional user-provided feedback about outcomes.
            
        Returns:
            Learning proposal with outcomes, learning drafts, and context update proposals.
        """
        try:
            proposal = learn_sync.initiate_learn_sync(
                feature_name=feature_name,
                changed_files=changed_files,
                test_results=test_results,
                execution_transcript=execution_transcript,
                user_feedback=user_feedback
            )
            
            # Serialize proposal
            return {
                "proposal_id": proposal.proposal_id,
                "feature_name": proposal.feature_name,
                "created_at": proposal.created_at,
                "outcome_summary": {
                    "what_implemented": proposal.outcome_summary.what_implemented,
                    "what_failed": proposal.outcome_summary.what_failed,
                    "unexpected_difficulties": proposal.outcome_summary.unexpected_difficulties,
                    "wrong_assumptions": proposal.outcome_summary.wrong_assumptions,
                    "discovered_constraints": proposal.outcome_summary.discovered_constraints,
                    "evidence_files": proposal.outcome_summary.evidence_files,
                    "evidence_logs": proposal.outcome_summary.evidence_logs,
                    "unknowns": proposal.outcome_summary.unknowns,
                },
                "learning_drafts": [
                    {
                        "learning_id": draft.learning_id,
                        "artifact_type": draft.artifact_type.value,
                        "title": draft.title,
                        "context": draft.context,
                        "evidence": draft.evidence,
                        "recommendation": draft.recommendation,
                        "related_intents": draft.related_intents,
                        "related_decisions": draft.related_decisions,
                        "confidence": draft.confidence.value,
                        "impact": draft.impact.value,
                        "status": draft.status,
                        "target_artifact": draft.target_artifact,
                    }
                    for draft in proposal.learning_drafts
                ],
                "context_updates": [
                    {
                        "artifact_type": update.artifact_type,
                        "artifact_path": update.artifact_path,
                        "update_type": update.update_type,
                        "proposed_content": update.proposed_content,
                        "rationale": update.rationale,
                        "status": update.status,
                    }
                    for update in proposal.context_updates
                ],
                "changelog_entry": {
                    "date": proposal.changelog_entry.date,
                    "what_changed": proposal.changelog_entry.what_changed,
                    "why_changed": proposal.changelog_entry.why_changed,
                    "related_features": proposal.changelog_entry.related_features,
                    "related_decisions": proposal.changelog_entry.related_decisions,
                    "learning_artifacts": proposal.changelog_entry.learning_artifacts,
                    "status": proposal.changelog_entry.status,
                } if proposal.changelog_entry else None,
            }
        except Exception as e:
            return {
                "error": f"Error initiating learn sync: {str(e)}",
            }
    
    @mcp.tool()
    def learn_sync_review(proposal_id: str) -> dict:
        """Review a learning proposal.
        
        Args:
            proposal_id: ID of the learning proposal.
            
        Returns:
            Full learning proposal details.
        """
        try:
            proposal = learn_sync.get_proposal(proposal_id)
            if not proposal:
                return {
                    "error": f"Proposal not found: {proposal_id}",
                }
            
            # Return same format as initiate
            return {
                "proposal_id": proposal.proposal_id,
                "feature_name": proposal.feature_name,
                "created_at": proposal.created_at,
                "outcome_summary": {
                    "what_implemented": proposal.outcome_summary.what_implemented,
                    "what_failed": proposal.outcome_summary.what_failed,
                    "unexpected_difficulties": proposal.outcome_summary.unexpected_difficulties,
                    "wrong_assumptions": proposal.outcome_summary.wrong_assumptions,
                    "discovered_constraints": proposal.outcome_summary.discovered_constraints,
                    "evidence_files": proposal.outcome_summary.evidence_files,
                    "evidence_logs": proposal.outcome_summary.evidence_logs,
                    "unknowns": proposal.outcome_summary.unknowns,
                },
                "learning_drafts": [
                    {
                        "learning_id": draft.learning_id,
                        "artifact_type": draft.artifact_type.value,
                        "title": draft.title,
                        "context": draft.context,
                        "evidence": draft.evidence,
                        "recommendation": draft.recommendation,
                        "related_intents": draft.related_intents,
                        "related_decisions": draft.related_decisions,
                        "confidence": draft.confidence.value,
                        "impact": draft.impact.value,
                        "status": draft.status,
                        "target_artifact": draft.target_artifact,
                    }
                    for draft in proposal.learning_drafts
                ],
                "context_updates": [
                    {
                        "artifact_type": update.artifact_type,
                        "artifact_path": update.artifact_path,
                        "update_type": update.update_type,
                        "proposed_content": update.proposed_content,
                        "rationale": update.rationale,
                        "status": update.status,
                    }
                    for update in proposal.context_updates
                ],
                "changelog_entry": {
                    "date": proposal.changelog_entry.date,
                    "what_changed": proposal.changelog_entry.what_changed,
                    "why_changed": proposal.changelog_entry.why_changed,
                    "related_features": proposal.changelog_entry.related_features,
                    "related_decisions": proposal.changelog_entry.related_decisions,
                    "learning_artifacts": proposal.changelog_entry.learning_artifacts,
                    "status": proposal.changelog_entry.status,
                } if proposal.changelog_entry else None,
            }
        except Exception as e:
            return {
                "error": f"Error reviewing proposal: {str(e)}",
            }
    
    @mcp.tool()
    def learn_sync_accept(
        proposal_id: str,
        learning_ids: Optional[list] = None,
        context_update_indices: Optional[list] = None,
        accept_changelog: bool = False
    ) -> dict:
        """Accept specific learning proposals (preview only - actual application requires explicit action).
        
        Args:
            proposal_id: ID of the learning proposal.
            learning_ids: Optional list of learning IDs to accept. If None, accepts all.
            context_update_indices: Optional list of context update indices to accept. If None, accepts all.
            accept_changelog: Whether to accept the changelog entry.
            
        Returns:
            Preview of what would be applied (actual application requires separate step).
        """
        try:
            proposal = learn_sync.get_proposal(proposal_id)
            if not proposal:
                return {
                    "error": f"Proposal not found: {proposal_id}",
                }
            
            # Determine what to accept
            accepted_learnings = []
            if learning_ids is None:
                accepted_learnings = proposal.learning_drafts
            else:
                accepted_learnings = [
                    draft for draft in proposal.learning_drafts
                    if draft.learning_id in learning_ids
                ]
            
            accepted_updates = []
            if context_update_indices is None:
                accepted_updates = proposal.context_updates
            else:
                accepted_updates = [
                    proposal.context_updates[i]
                    for i in context_update_indices
                    if 0 <= i < len(proposal.context_updates)
                ]
            
            # Return preview (actual application would happen in learn_sync_apply)
            return {
                "proposal_id": proposal_id,
                "accepted_learnings": [
                    {
                        "learning_id": draft.learning_id,
                        "title": draft.title,
                        "artifact_type": draft.artifact_type.value,
                    }
                    for draft in accepted_learnings
                ],
                "accepted_context_updates": [
                    {
                        "artifact_type": update.artifact_type,
                        "artifact_path": update.artifact_path,
                        "update_type": update.update_type,
                    }
                    for update in accepted_updates
                ],
                "changelog_accepted": accept_changelog,
                "note": "This is a preview. Use learn_sync_apply to actually apply changes.",
            }
        except Exception as e:
            return {
                "error": f"Error accepting proposal: {str(e)}",
            }
    
    @mcp.tool()
    def learn_sync_apply(
        proposal_id: str,
        learning_ids: Optional[list] = None,
        context_update_indices: Optional[list] = None,
        apply_changelog: bool = False,
        confirm: bool = False
    ) -> dict:
        """Apply accepted learnings to context artifacts (requires explicit confirmation).
        
        WARNING: This will modify context files. Only call with confirm=True after human review.
        
        Args:
            proposal_id: ID of the learning proposal.
            learning_ids: Optional list of learning IDs to apply. If None, applies all.
            context_update_indices: Optional list of context update indices to apply. If None, applies all.
            apply_changelog: Whether to apply the changelog entry.
            confirm: Must be True to actually apply changes.
            
        Returns:
            Result of applying learnings.
        """
        if not confirm:
            return {
                "error": "Application requires explicit confirmation. Set confirm=True.",
                "note": "This tool will modify context files. Review proposals first using learn_sync_review.",
            }
        
        try:
            proposal = learn_sync.get_proposal(proposal_id)
            if not proposal:
                return {
                    "error": f"Proposal not found: {proposal_id}",
                }
            
            # For v1, return instructions rather than actually modifying files
            # (per Decision 006 and evolution rules, file mutations should be explicit)
            applied = []
            
            if learning_ids is None:
                learning_ids = [draft.learning_id for draft in proposal.learning_drafts]
            
            for learning_id in learning_ids:
                draft = next(
                    (d for d in proposal.learning_drafts if d.learning_id == learning_id),
                    None
                )
                if draft:
                    applied.append({
                        "learning_id": learning_id,
                        "action": f"Create {draft.artifact_type.value} artifact",
                        "title": draft.title,
                    })
            
            if context_update_indices is None:
                context_update_indices = list(range(len(proposal.context_updates)))
            
            for idx in context_update_indices:
                if 0 <= idx < len(proposal.context_updates):
                    update = proposal.context_updates[idx]
                    applied.append({
                        "context_update_index": idx,
                        "action": f"Update {update.artifact_type} at {update.artifact_path}",
                        "update_type": update.update_type,
                    })
            
            if apply_changelog and proposal.changelog_entry:
                applied.append({
                    "action": "Append changelog entry",
                    "date": proposal.changelog_entry.date,
                })
            
            return {
                "proposal_id": proposal_id,
                "applied": applied,
                "note": "In v1, this returns instructions. Actual file mutations should be performed explicitly by the user or agent with proper approval.",
            }
        except Exception as e:
            return {
                "error": f"Error applying proposal: {str(e)}",
            }
    
    # Prompt Pack Management Tools (Decision 010)
    
    @mcp.tool()
    def hub_prompts_status() -> dict:
        """Get current prompt pack status.
        
        Returns:
            Dict with current pack, cached versions, and bundled version.
        """
        try:
            return pack_manager.status()
        except Exception as e:
            return {
                "error": f"Error getting prompt pack status: {str(e)}",
            }
    
    @mcp.tool()
    def hub_prompts_install(
        pack_name: str,
        version: str,
        url: Optional[str] = None
    ) -> dict:
        """Install a prompt pack from URL.
        
        Args:
            pack_name: Pack name (e.g., "context-mesh-core").
            version: Pack version (e.g., "1.10.0").
            url: Optional download URL. If None, uses GitHub release pattern.
        
        Returns:
            Dict with success status and message.
        """
        try:
            return pack_manager.install(pack_name, version, url)
        except Exception as e:
            return {
                "error": f"Error installing prompt pack: {str(e)}",
            }
    
    @mcp.tool()
    def hub_prompts_use(
        pack_name: str,
        version: str,
        source: str = "cached"
    ) -> dict:
        """Pin a prompt pack version in manifest.
        
        Args:
            pack_name: Pack name.
            version: Pack version.
            source: Source type ("cached" or "bundled").
        
        Returns:
            Dict with success status.
        """
        try:
            return pack_manager.use(pack_name, version, source)
        except Exception as e:
            return {
                "error": f"Error pinning prompt pack: {str(e)}",
            }
    
    @mcp.tool()
    def hub_prompts_verify(pack_name: str, version: str) -> dict:
        """Verify prompt pack integrity.
        
        Args:
            pack_name: Pack name.
            version: Pack version.
        
        Returns:
            Dict with verification results.
        """
        try:
            return pack_manager.verify(pack_name, version)
        except Exception as e:
            return {
                "error": f"Error verifying prompt pack: {str(e)}",
            }
    
    # Prompt-Driven Intent/Build/Learn Tools (Decision 010)
    
    def _render_template_with_context(
        template_name: str, inputs: dict, context_bundle: Optional[dict] = None
    ) -> dict:
        """Render a prompt template with inputs and context.
        
        Args:
            template_name: Template filename (e.g., "add-feature.md").
            inputs: User inputs for template.
            context_bundle: Optional context bundle (scoped per Decision 003).
        
        Returns:
            Dict with rendered content and provenance.
        """
        content, provenance = prompt_resolver.resolve_template(template_name)
        
        if content is None:
            return {
                "error": f"Template not found: {template_name}",
                "note": "Check that template exists in repo override, cached pack, or bundled fallback.",
            }
        
        # For v1, return template content + inputs + provenance
        # Actual rendering/execution happens in agent layer
        return {
            "template": template_name,
            "content": content,
            "inputs": inputs,
            "contextBundle": context_bundle,
            "provenance": provenance,
            "note": "Template resolved. Use this content to generate Context Mesh artifacts.",
        }
    
    @mcp.tool()
    def intent_new_project(inputs: dict, context_bundle: Optional[dict] = None) -> dict:
        """Create new project setup using new-project.md template.
        
        Args:
            inputs: Project setup inputs (name, description, etc.).
            context_bundle: Optional scoped context bundle.
        
        Returns:
            Rendered template with provenance.
        """
        return _render_template_with_context("new-project.md", inputs, context_bundle)
    
    @mcp.tool()
    def intent_existing_project(
        inputs: dict, context_bundle: Optional[dict] = None
    ) -> dict:
        """Bootstrap existing project using existing-project.md template.
        
        Args:
            inputs: Project bootstrap inputs.
            context_bundle: Optional scoped context bundle.
        
        Returns:
            Rendered template with provenance.
        """
        return _render_template_with_context("existing-project.md", inputs, context_bundle)
    
    @mcp.tool()
    def intent_add_feature(
        feature_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None
    ) -> dict:
        """Add a new feature using add-feature.md template.
        
        Args:
            feature_name: Name of the feature.
            inputs: Feature inputs (what, why, acceptance criteria).
            context_bundle: Optional scoped context bundle (per Decision 003).
        
        Returns:
            Rendered template with provenance. Use to generate feature intent.
        """
        inputs["feature_name"] = feature_name
        result = _render_template_with_context("add-feature.md", inputs, context_bundle)
        
        # Add note about artifact generation
        if "error" not in result:
            result["note"] = (
                "Template resolved. Generate context/intent/feature-{name}.md "
                "following the template structure. Record provenance in artifact."
            )
        
        return result
    
    @mcp.tool()
    def intent_update_feature(
        feature_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None
    ) -> dict:
        """Update an existing feature using update-feature.md template.
        
        Args:
            feature_name: Name of the feature to update.
            inputs: Update inputs (changes to apply).
            context_bundle: Optional scoped context bundle.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["feature_name"] = feature_name
        return _render_template_with_context("update-feature.md", inputs, context_bundle)
    
    @mcp.tool()
    def intent_fix_bug(
        bug_description: str,
        inputs: dict,
        context_bundle: Optional[dict] = None
    ) -> dict:
        """Fix a bug using fix-bug.md template.
        
        Args:
            bug_description: Description of the bug.
            inputs: Bug fix inputs (impact, approach, related feature).
            context_bundle: Optional scoped context bundle.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["bug_description"] = bug_description
        return _render_template_with_context("fix-bug.md", inputs, context_bundle)
    
    @mcp.tool()
    def intent_create_agent(
        agent_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None
    ) -> dict:
        """Create a new agent using create-agent.md template.
        
        Args:
            agent_name: Name of the agent.
            inputs: Agent inputs (purpose, steps, DoD).
            context_bundle: Optional scoped context bundle.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["agent_name"] = agent_name
        return _render_template_with_context("create-agent.md", inputs, context_bundle)
    
    @mcp.tool()
    def learn_sync(
        feature_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None
    ) -> dict:
        """Sync learnings using learn-update.md template.
        
        Args:
            feature_name: Name of completed feature.
            inputs: Learning inputs (outcomes, learnings, evidence).
            context_bundle: Optional scoped context bundle.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["feature_name"] = feature_name
        return _render_template_with_context("learn-update.md", inputs, context_bundle)
