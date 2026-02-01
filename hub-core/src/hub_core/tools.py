"""MCP tool definitions for Hub Core."""

from typing import Optional, Dict, Any
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


def _get_components_for_repo(
    repo_root: Optional[str],
    default_components: Dict[str, Any],
) -> Dict[str, Any]:
    """Get loader, validator, bundler, etc. for the given repo_root, or return defaults.
    
    When repo_root is provided, creates fresh components for that path so the MCP
    can work with any project. When None, returns the server's default components.
    """
    if not repo_root or not str(repo_root).strip():
        return default_components
    path = Path(repo_root).resolve()
    _loader = ContextLoader(path)
    _loader.load()
    _validator = ContextValidator(_loader)
    _bundler = ContextBundler(_loader) if (path / "context").exists() else None
    _build_protocol = BuildProtocol(_loader, _bundler) if _bundler else None
    _learn_sync = LearnSync(_loader)
    _scanner = RepositoryScanner(path)
    _slice_generator = SliceGenerator(_scanner)
    _context_extractor = ContextExtractor(_scanner)
    _prompt_resolver = PromptResolver(path)
    _pack_manager = PromptPackManager(path)
    return {
        "loader": _loader,
        "validator": _validator,
        "bundler": _bundler,
        "build_protocol": _build_protocol,
        "learn_sync": _learn_sync,
        "scanner": _scanner,
        "slice_generator": _slice_generator,
        "context_extractor": _context_extractor,
        "prompt_resolver": _prompt_resolver,
        "pack_manager": _pack_manager,
    }


def create_tools(mcp: FastMCP, repo_root: Optional[Path] = None):
    """Register MCP tools with the server.
    
    Args:
        mcp: FastMCP server instance.
        repo_root: Optional repository root path. Auto-detects if None.
    """
    # Use provided repo_root or current directory
    effective_repo_root = repo_root or Path.cwd()
    
    loader = ContextLoader(effective_repo_root)
    validator = ContextValidator(loader)
    
    # Only create bundler if context/ exists (it requires loaded index)
    bundler = None
    build_protocol = None
    learn_sync = None
    
    scanner = RepositoryScanner(effective_repo_root)
    slice_generator = SliceGenerator(scanner)
    context_extractor = ContextExtractor(scanner)
    prompt_resolver = PromptResolver(effective_repo_root)
    pack_manager = PromptPackManager(effective_repo_root)
    
    # Load context index on startup (now returns empty index if no context/)
    try:
        loader.load()
        # Only create bundler/build_protocol if context loaded successfully
        if loader.context_dir.exists():
            bundler = ContextBundler(loader)
            build_protocol = BuildProtocol(loader, bundler)
            learn_sync = LearnSync(loader)
    except Exception as e:
        # Index will be loaded lazily on first tool call if needed
        pass
    
    default_components = {
        "loader": loader,
        "validator": validator,
        "bundler": bundler,
        "build_protocol": build_protocol,
        "learn_sync": learn_sync,
        "scanner": scanner,
        "slice_generator": slice_generator,
        "context_extractor": context_extractor,
        "prompt_resolver": prompt_resolver,
        "pack_manager": pack_manager,
    }
    
    @mcp.tool()
    def context_read(
        artifact_type: str,
        name: str,
        repo_root: Optional[str] = None
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
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path so the MCP works with that project's context.
        
        Returns:
            Dictionary with artifact content and metadata.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            index = loader_.index
            
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
    def context_validate(repo_root: Optional[str] = None) -> dict:
        """Validate Context Mesh repository structure and content.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path so the MCP validates that project's context.
        
        Returns:
            Dictionary with validation results (errors, warnings, info).
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            validator_ = comp["validator"]
            result = validator_.validate()
            
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
        identifier: str,
        repo_root: Optional[str] = None
    ) -> dict:
        """Generate a context bundle.
        
        Args:
            bundle_type: Type of bundle: "project", "feature", or "decision".
            identifier:
                - For "project": ignored (use "project")
                - For "feature": feature name (e.g., "hub-core")
                - For "decision": decision number (e.g., "001")
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to bundle that project's context.
        
        Returns:
            Dictionary with bundle content and metadata.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        bundler_ = comp["bundler"]
        if bundler_ is None:
            return {
                "error": "Context Mesh not initialized. Use cm_new_project() or cm_init() first.",
                "tip": "Create context/ directory to enable bundling.",
            }
        
        try:
            if bundle_type == "project":
                bundle = bundler_.bundle_project()
            elif bundle_type == "feature":
                bundle = bundler_.bundle_feature(identifier)
            elif bundle_type == "decision":
                bundle = bundler_.bundle_decision(identifier)
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
    def hub_health(repo_root: Optional[str] = None) -> dict:
        """Health check for Hub Core MCP server.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to check that project's context status.
        
        Returns:
            Dictionary with server status, repository root, and context index status.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            index = loader_.index
            repo_root_str = str(loader_.repo_root)
            
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
                "context_dir": str(loader_.context_dir),
                "index_loaded": loader_._loaded,
                "artifact_counts": stats,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    @mcp.tool()
    def build_plan(feature_name: str, repo_root: Optional[str] = None) -> dict:
        """Generate a build plan for a feature.
        
        Args:
            feature_name: Name of the feature (e.g., "hub-core").
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to plan for that project's features.
        
        Returns:
            Dictionary with build plan details.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        build_protocol_ = comp["build_protocol"]
        if build_protocol_ is None:
            return {
                "error": "Context Mesh not initialized. Use cm_new_project() or cm_init() first.",
                "tip": "Create context/ directory with features to enable build planning.",
            }
        
        try:
            plan = build_protocol_.create_plan(feature_name)
            
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
        feedback: Optional[str] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Approve or reject a build plan.
        
        Args:
            plan_id: Plan ID to approve/reject.
            action: "approve" or "reject".
            scope: Optional list of step numbers for partial approval.
            feedback: Optional feedback message.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dictionary with approval status.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        build_protocol_ = comp["build_protocol"]
        if build_protocol_ is None:
            return {
                "error": "Context Mesh not initialized.",
                "tip": "Create context/ directory first.",
            }
        
        try:
            approval = build_protocol_.approve_plan(
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
        mode: str = "instruction",
        repo_root: Optional[str] = None
    ) -> dict:
        """Generate execution instructions from an approved plan.
        
        Args:
            plan_id: Plan ID to generate instructions for.
            mode: Execution mode ("instruction" or "assisted").
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dictionary with execution instructions.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        build_protocol_ = comp["build_protocol"]
        if build_protocol_ is None:
            return {
                "error": "Context Mesh not initialized.",
                "tip": "Create context/ directory first.",
            }
        
        try:
            instructions = build_protocol_.generate_instructions(plan_id, mode)
            
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
    def brownfield_scan(path: Optional[str] = None, repo_root: Optional[str] = None) -> dict:
        """Scan repository structure for brownfield analysis.
        
        Args:
            path: Optional path to scan (defaults to repository root).
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to scan that project.
        
        Returns:
            Dictionary with structural analysis results.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            scanner_ = comp["scanner"]
            scan_path = Path(path) if path else scanner_.repo_root
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
    def brownfield_slice(strategy: str = "directory", repo_root: Optional[str] = None) -> dict:
        """Generate repository slices for brownfield analysis.
        
        Args:
            strategy: Slice strategy ("directory", "module", "language").
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to slice that project.
        
        Returns:
            Dictionary with slice definitions.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            slice_generator_ = comp["slice_generator"]
            slices = slice_generator_.generate_slices(strategy)
            
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
    def brownfield_extract(slice_id: Optional[str] = None, path: Optional[str] = None, repo_root: Optional[str] = None) -> dict:
        """Extract proposed context artifacts from a repository slice.
        
        Args:
            slice_id: Slice ID to extract from (from brownfield_slice).
            path: Alternative: path to extract from (creates temporary slice).
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to extract from that project.
        
        Returns:
            Dictionary with proposed context artifacts.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            slice_generator_ = comp["slice_generator"]
            context_extractor_ = comp["context_extractor"]
            if slice_id:
                # Find slice by ID
                slices = slice_generator_.generate_slices()
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
            
            artifacts = context_extractor_.extract_from_slice(slice_def)
            
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
    def brownfield_report(slice_filter: Optional[str] = None, repo_root: Optional[str] = None) -> dict:
        """Generate comprehensive brownfield analysis report.
        
        Args:
            slice_filter: Optional slice ID to filter report (defaults to all slices).
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to generate report for that project.
        
        Returns:
            Dictionary with comprehensive brownfield report.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            scanner_ = comp["scanner"]
            slice_generator_ = comp["slice_generator"]
            context_extractor_ = comp["context_extractor"]
            
            # Scan repository
            analysis = scanner_.scan()
            
            # Generate slices
            slices = slice_generator_.generate_slices()
            
            # Extract from slices
            all_artifacts = []
            for slice_def in slices:
                if slice_filter and slice_def.slice_id != slice_filter:
                    continue
                artifacts = context_extractor_.extract_from_slice(slice_def)
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
        user_feedback: Optional[str] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Initiate Learn Sync for a feature after execution.
        
        Args:
            feature_name: Name of the feature (e.g., "hub-core").
            changed_files: Optional list of changed file paths.
            test_results: Optional test results summary.
            execution_transcript: Optional execution transcript.
            user_feedback: Optional user-provided feedback about outcomes.
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to use that project's context.
            
        Returns:
            Learning proposal with outcomes, learning drafts, and context update proposals.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        learn_sync_ = comp["learn_sync"]
        if learn_sync_ is None:
            return {
                "error": "Context Mesh not initialized.",
                "tip": "Create context/ directory with features first.",
            }
        
        try:
            proposal = learn_sync_.initiate_learn_sync(
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
    def learn_sync_review(proposal_id: str, repo_root: Optional[str] = None) -> dict:
        """Review a learning proposal.
        
        Args:
            proposal_id: ID of the learning proposal.
            repo_root: Path to the repository root. If not provided, uses server default.
            
        Returns:
            Full learning proposal details.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        learn_sync_ = comp["learn_sync"]
        if learn_sync_ is None:
            return {
                "error": "Context Mesh not initialized.",
            }
        
        try:
            proposal = learn_sync_.get_proposal(proposal_id)
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
        accept_changelog: bool = False,
        repo_root: Optional[str] = None
    ) -> dict:
        """Accept specific learning proposals (preview only - actual application requires explicit action).
        
        Args:
            proposal_id: ID of the learning proposal.
            learning_ids: Optional list of learning IDs to accept. If None, accepts all.
            context_update_indices: Optional list of context update indices to accept. If None, accepts all.
            accept_changelog: Whether to accept the changelog entry.
            repo_root: Path to the repository root. If not provided, uses server default.
            
        Returns:
            Preview of what would be applied (actual application requires separate step).
        """
        comp = _get_components_for_repo(repo_root, default_components)
        learn_sync_ = comp["learn_sync"]
        if learn_sync_ is None:
            return {"error": "Context Mesh not initialized."}
        
        try:
            proposal = learn_sync_.get_proposal(proposal_id)
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
        confirm: bool = False,
        repo_root: Optional[str] = None
    ) -> dict:
        """Apply accepted learnings to context artifacts (requires explicit confirmation).
        
        WARNING: This will modify context files. Only call with confirm=True after human review.
        
        Args:
            proposal_id: ID of the learning proposal.
            learning_ids: Optional list of learning IDs to apply. If None, applies all.
            context_update_indices: Optional list of context update indices to apply. If None, applies all.
            apply_changelog: Whether to apply the changelog entry.
            confirm: Must be True to actually apply changes.
            repo_root: Path to the repository root. If not provided, uses server default.
            
        Returns:
            Result of applying learnings.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        learn_sync_ = comp["learn_sync"]
        if learn_sync_ is None:
            return {"error": "Context Mesh not initialized."}
        
        if not confirm:
            return {
                "error": "Application requires explicit confirmation. Set confirm=True.",
                "note": "This tool will modify context files. Review proposals first using learn_sync_review.",
            }
        
        try:
            proposal = learn_sync_.get_proposal(proposal_id)
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
    def hub_prompts_status(repo_root: Optional[str] = None) -> dict:
        """Get current prompt pack status.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dict with current pack, cached versions, and bundled version.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            pack_manager_ = comp["pack_manager"]
            return pack_manager_.status()
        except Exception as e:
            return {
                "error": f"Error getting prompt pack status: {str(e)}",
            }
    
    @mcp.tool()
    def hub_prompts_install(
        pack_name: str,
        version: str,
        url: Optional[str] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Install a prompt pack from URL.
        
        Args:
            pack_name: Pack name (e.g., "context-mesh-core").
            version: Pack version (e.g., "1.10.0").
            url: Optional download URL. If None, uses GitHub release pattern.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dict with success status and message.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            pack_manager_ = comp["pack_manager"]
            return pack_manager_.install(pack_name, version, url)
        except Exception as e:
            return {
                "error": f"Error installing prompt pack: {str(e)}",
            }
    
    @mcp.tool()
    def hub_prompts_use(
        pack_name: str,
        version: str,
        source: str = "cached",
        repo_root: Optional[str] = None
    ) -> dict:
        """Pin a prompt pack version in manifest.
        
        Args:
            pack_name: Pack name.
            version: Pack version.
            source: Source type ("cached" or "bundled").
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dict with success status.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            pack_manager_ = comp["pack_manager"]
            return pack_manager_.use(pack_name, version, source)
        except Exception as e:
            return {
                "error": f"Error pinning prompt pack: {str(e)}",
            }
    
    @mcp.tool()
    def hub_prompts_verify(pack_name: str, version: str, repo_root: Optional[str] = None) -> dict:
        """Verify prompt pack integrity.
        
        Args:
            pack_name: Pack name.
            version: Pack version.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dict with verification results.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            pack_manager_ = comp["pack_manager"]
            return pack_manager_.verify(pack_name, version)
        except Exception as e:
            return {
                "error": f"Error verifying prompt pack: {str(e)}",
            }
    
    # Prompt-Driven Intent/Build/Learn Tools (Decision 010)
    
    def _render_template_with_context(
        template_name: str, inputs: dict, context_bundle: Optional[dict] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Render a prompt template with inputs and context.
        
        Args:
            template_name: Template filename (e.g., "add-feature.md").
            inputs: User inputs for template.
            context_bundle: Optional context bundle (scoped per Decision 003).
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Dict with rendered content and provenance.
        """
        comp = _get_components_for_repo(repo_root, default_components)
        prompt_resolver_ = comp["prompt_resolver"]
        content, provenance = prompt_resolver_.resolve_template(template_name)
        
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
    def intent_new_project(inputs: dict, context_bundle: Optional[dict] = None, repo_root: Optional[str] = None) -> dict:
        """Create new project setup using new-project.md template.
        
        Args:
            inputs: Project setup inputs (name, description, etc.).
            context_bundle: Optional scoped context bundle.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance.
        """
        return _render_template_with_context("new-project.md", inputs, context_bundle, repo_root)
    
    @mcp.tool()
    def intent_existing_project(
        inputs: dict, context_bundle: Optional[dict] = None, repo_root: Optional[str] = None
    ) -> dict:
        """Bootstrap existing project using existing-project.md template.
        
        Args:
            inputs: Project bootstrap inputs.
            context_bundle: Optional scoped context bundle.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance.
        """
        return _render_template_with_context("existing-project.md", inputs, context_bundle, repo_root)
    
    @mcp.tool()
    def intent_add_feature(
        feature_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Add a new feature using add-feature.md template.
        
        Args:
            feature_name: Name of the feature.
            inputs: Feature inputs (what, why, acceptance criteria).
            context_bundle: Optional scoped context bundle (per Decision 003).
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance. Use to generate feature intent.
        """
        inputs["feature_name"] = feature_name
        result = _render_template_with_context("add-feature.md", inputs, context_bundle, repo_root)
        
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
        context_bundle: Optional[dict] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Update an existing feature using update-feature.md template.
        
        Args:
            feature_name: Name of the feature to update.
            inputs: Update inputs (changes to apply).
            context_bundle: Optional scoped context bundle.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["feature_name"] = feature_name
        return _render_template_with_context("update-feature.md", inputs, context_bundle, repo_root)
    
    @mcp.tool()
    def intent_fix_bug(
        bug_description: str,
        inputs: dict,
        context_bundle: Optional[dict] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Fix a bug using fix-bug.md template.
        
        Args:
            bug_description: Description of the bug.
            inputs: Bug fix inputs (impact, approach, related feature).
            context_bundle: Optional scoped context bundle.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["bug_description"] = bug_description
        return _render_template_with_context("fix-bug.md", inputs, context_bundle, repo_root)
    
    @mcp.tool()
    def intent_create_agent(
        agent_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Create a new agent using create-agent.md template.
        
        Args:
            agent_name: Name of the agent.
            inputs: Agent inputs (purpose, steps, DoD).
            context_bundle: Optional scoped context bundle.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["agent_name"] = agent_name
        return _render_template_with_context("create-agent.md", inputs, context_bundle, repo_root)
    
    @mcp.tool()
    def learn_sync(
        feature_name: str,
        inputs: dict,
        context_bundle: Optional[dict] = None,
        repo_root: Optional[str] = None
    ) -> dict:
        """Sync learnings using learn-update.md template.
        
        Args:
            feature_name: Name of completed feature.
            inputs: Learning inputs (outcomes, learnings, evidence).
            context_bundle: Optional scoped context bundle.
            repo_root: Path to the repository root. If not provided, uses server default.
        
        Returns:
            Rendered template with provenance.
        """
        inputs["feature_name"] = feature_name
        return _render_template_with_context("learn-update.md", inputs, context_bundle, repo_root)
    
    # ============================================
    # CHAT-FIRST TOOLS (High-Level Experience)
    # ============================================
    # These tools provide a conversational interface for Context Mesh.
    # Users can interact naturally: "help me start a new project" or "add a feature"
    
    @mcp.tool()
    def cm_help() -> dict:
        """Show what you can do with Context Mesh Hub.
        
        Use this when you want to know available commands and workflows.
        Returns a friendly, conversational guide.
        
        Returns:
            Dictionary with conversational help and guidance.
        """
        return {
            "welcome": "👋 Welcome to Context Mesh Hub!",
            "tagline": "Your Operational System of Context for AI-assisted development",
            "how_it_works": (
                "Context Mesh uses a simple 3-step workflow:\n"
                "  1. **Intent** - Define WHAT you're building and WHY\n"
                "  2. **Build** - AI helps implement while you supervise\n"
                "  3. **Learn** - Update context with what you learned"
            ),
            "getting_started": {
                "new_project": {
                    "say": "I want to start a new project",
                    "or": "Create a new project called [name]",
                    "description": "I'll ask you some questions and set up the context/ structure"
                },
                "existing_project": {
                    "say": "Add Context Mesh to my existing project",
                    "or": "Help me document my codebase",
                    "description": "I'll analyze your code and create initial context"
                },
                "check_status": {
                    "say": "What's the status of my project?",
                    "or": "Show me the current state",
                    "description": "I'll show you what's been created and what's next"
                },
            },
            "daily_workflows": {
                "add_feature": {
                    "say": "I want to add a feature for user authentication",
                    "description": "I'll guide you through documenting what, why, and acceptance criteria"
                },
                "update_feature": {
                    "say": "Update the user-auth feature",
                    "description": "I'll help you modify an existing feature intent"
                },
                "fix_bug": {
                    "say": "I need to fix a bug with login",
                    "description": "I'll help you document and track the bug fix"
                },
                "create_decision": {
                    "say": "We decided to use PostgreSQL for the database",
                    "description": "I'll help you document this technical decision (ADR)"
                },
                "create_agent": {
                    "say": "Create an agent for API development",
                    "description": "I'll help you create a reusable execution pattern"
                },
                "list_features": {
                    "say": "Show me all features",
                    "description": "I'll list all feature intents and their status"
                },
                "list_decisions": {
                    "say": "Show me all decisions",
                    "description": "I'll list all technical decisions (ADRs)"
                },
            },
            "build_phase": {
                "description": "When you're ready to implement:",
                "plan": "Say: 'Create a build plan for [feature]' - I'll generate an implementation plan",
                "approve": "Review the plan and say 'Approve' or request changes",
                "execute": "Say: 'Execute the plan' - I'll provide step-by-step instructions",
            },
            "learn_phase": {
                "description": "After implementation:",
                "sync": "Say: 'Sync learnings for [feature]' - I'll help capture what you learned",
                "update": "I'll suggest updates to decisions, patterns, and changelog",
            },
            "quick_tip": "Just tell me what you want to do in natural language. For example: 'I want to add a dark mode feature' or 'Help me document my existing code'",
        }
    
    @mcp.tool()
    def cm_status(repo_root: Optional[str] = None) -> dict:
        """Get the current status of your Context Mesh project.
        
        Shows validation results, artifact counts, and guidance on next steps.
        Works even if context/ doesn't exist yet (helps with greenfield projects).
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to check that project's status.
        
        Returns:
            Dictionary with project status, validation, and recommendations.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            
            # Check if context/ exists
            context_exists = loader_.context_dir.exists()
            
            if not context_exists:
                # Greenfield project - no context yet
                return {
                    "project": {
                        "repo_root": str(loader_.repo_root),
                        "context_mesh_initialized": False,
                        "lifecycle_phase": "Not Initialized",
                    },
                    "artifacts": {
                        "project_intent": "✗ Not created",
                        "feature_intents": 0,
                        "decisions": 0,
                        "patterns": 0,
                        "agents": 0,
                        "changelog": "✗ Not created",
                    },
                    "guidance": {
                        "current_phase": "Setup",
                        "next_step": "Use cm_new_project() or cm_init() to create Context Mesh structure",
                        "options": [
                            "cm_new_project(name='...', description='...', why='...') - Full setup with details",
                            "cm_init() - Quick minimal setup",
                            "cm_existing_project() - Add Context Mesh to existing codebase",
                        ],
                    },
                    "tip": "Say 'Create a new project called X' and I'll set up Context Mesh for you!",
                }
            
            # Get health info
            index = loader_.index
            validator_ = comp["validator"]
            
            # Count artifacts
            feature_count = len(index["feature_intents"])
            decision_count = len(index["decisions"])
            pattern_count = len(index["knowledge"]["patterns"])
            agent_count = len(index["agents"])
            has_project_intent = index.get("project_intent") is not None
            has_changelog = index.get("changelog") is not None
            
            # Get validation
            validation_result = validator_.validate()
            
            # Determine lifecycle phase
            if not has_project_intent:
                phase = "Partial Setup"
                phase_guidance = "Create project-intent.md to complete setup"
            elif feature_count == 0:
                phase = "Intent"
                phase_guidance = "Add your first feature with cm_add_feature()"
            elif validation_result.valid:
                phase = "Ready to Build"
                phase_guidance = "Use build_plan() to create implementation plan"
            else:
                phase = "Needs Attention"
                phase_guidance = f"Fix {len(validation_result.errors)} validation errors"
            
            # Build status response
            status = {
                "project": {
                    "repo_root": str(loader_.repo_root),
                    "context_mesh_initialized": has_project_intent,
                    "lifecycle_phase": phase,
                },
                "artifacts": {
                    "project_intent": "✓" if has_project_intent else "✗ Missing",
                    "feature_intents": feature_count,
                    "decisions": decision_count,
                    "patterns": pattern_count,
                    "agents": agent_count,
                    "changelog": "✓" if has_changelog else "✗ Missing",
                },
                "validation": {
                    "valid": validation_result.valid,
                    "errors": len(validation_result.errors),
                    "warnings": len(validation_result.warnings),
                    "details": [
                        {"level": "error", "message": e.message}
                        for e in validation_result.errors[:3]  # Show top 3
                    ] + [
                        {"level": "warning", "message": w.message}
                        for w in validation_result.warnings[:2]  # Show top 2
                    ],
                },
                "guidance": {
                    "current_phase": phase,
                    "next_step": phase_guidance,
                    "tip": "Use cm_help() to see all available commands",
                },
            }
            
            return status
            
        except Exception as e:
            return {
                "error": f"Error getting status: {str(e)}",
                "tip": "Try cm_new_project() or cm_init() to create Context Mesh structure",
            }
    
    @mcp.tool()
    def cm_list_features(repo_root: Optional[str] = None) -> dict:
        """List all feature intents in the project.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to list that project's features.
        
        Returns:
            Dictionary with all features, their status, and paths.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            index = loader_.index
            features = []
            
            for name, artifact in index["feature_intents"].items():
                content = artifact.get("content", "")
                
                # Extract status from content
                status = "Unknown"
                if "Status: Active" in content or "Status**: Active" in content:
                    status = "Active"
                elif "Status: Completed" in content or "Status**: Completed" in content:
                    status = "Completed"
                elif "Status: Draft" in content or "Status**: Draft" in content:
                    status = "Draft"
                elif "Status: Blocked" in content or "Status**: Blocked" in content:
                    status = "Blocked"
                
                # Extract "What" section (first paragraph after ## What)
                what_summary = ""
                if "## What" in content:
                    what_section = content.split("## What")[1].split("##")[0]
                    what_summary = what_section.strip()[:100] + "..." if len(what_section.strip()) > 100 else what_section.strip()
                
                features.append({
                    "name": name,
                    "status": status,
                    "path": artifact.get("path", ""),
                    "summary": what_summary,
                })
            
            return {
                "total": len(features),
                "features": features,
                "tip": "Use context_read(artifact_type='feature_intent', name='feature-name') to see full details",
            }
            
        except Exception as e:
            return {
                "error": f"Error listing features: {str(e)}",
            }
    
    @mcp.tool()
    def cm_list_decisions(repo_root: Optional[str] = None) -> dict:
        """List all decisions (ADRs) in the project.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to list that project's decisions.
        
        Returns:
            Dictionary with all decisions, their status, and titles.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            index = loader_.index
            decisions = []
            
            for number, artifact in index["decisions"].items():
                content = artifact.get("content", "")
                
                # Extract title from first heading
                title = ""
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                
                # Extract status
                status = "Unknown"
                if "Status: Accepted" in content or "Status**: Accepted" in content:
                    status = "Accepted"
                elif "Status: Proposed" in content or "Status**: Proposed" in content:
                    status = "Proposed"
                elif "Status: Deprecated" in content or "Status**: Deprecated" in content:
                    status = "Deprecated"
                elif "Status: Superseded" in content or "Status**: Superseded" in content:
                    status = "Superseded"
                
                decisions.append({
                    "number": number,
                    "title": title,
                    "status": status,
                    "path": artifact.get("path", ""),
                })
            
            # Sort by number
            decisions.sort(key=lambda x: x["number"])
            
            return {
                "total": len(decisions),
                "decisions": decisions,
                "tip": "Use context_read(artifact_type='decision', name='001') to see full details",
            }
            
        except Exception as e:
            return {
                "error": f"Error listing decisions: {str(e)}",
            }
    
    @mcp.tool()
    def cm_add_feature(repo_root: Optional[str] = None) -> dict:
        """Start adding a new feature to the project.
        
        Returns a conversational prompt that guides through:
        1. Feature name
        2. What it does and why
        3. Acceptance criteria
        4. Technical approach (creates decision/ADR)
        
        The AI agent uses this prompt to ask questions and create the files.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to add feature to that project.
        
        Returns:
            Dictionary with prompt template and instructions.
        
        Example usage in chat:
            User: "I want to add a feature for user authentication"
            AI: calls cm_add_feature() → gets the prompt → asks questions
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            prompt_resolver_ = comp["prompt_resolver"]
            # Resolve the add-feature.md template
            content, provenance = prompt_resolver_.resolve_template("add-feature.md")
            
            if content is None:
                return {
                    "error": "Template add-feature.md not found",
                    "tip": "Check prompt-packs installation with hub_prompts_status()",
                }
            
            return {
                "action": "add_feature",
                "prompt_template": content,
                "provenance": provenance,
                "instructions": (
                    "Use the prompt template above to guide the conversation. "
                    "Ask the user the questions listed, then create the feature intent "
                    "and decision files based on their answers."
                ),
                "files_to_create": [
                    "context/intent/feature-[name].md",
                    "context/decisions/[number]-[name].md",
                ],
                "tip": "Ask questions one at a time for better UX",
            }
            
        except Exception as e:
            return {
                "error": f"Error loading add-feature prompt: {str(e)}",
            }
    
    @mcp.tool()
    def cm_fix_bug(repo_root: Optional[str] = None) -> dict:
        """Start documenting a bug fix.
        
        Returns a conversational prompt that guides through:
        1. Bug description
        2. Expected vs actual behavior
        3. Impact and root cause
        4. Related feature
        
        The AI agent uses this prompt to ask questions and create the bug intent.
        
        Returns:
            Dictionary with prompt template and instructions.
        
        Example usage in chat:
            User: "I need to fix a bug with login"
            AI: calls cm_fix_bug() → gets the prompt → asks questions
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            prompt_resolver_ = comp["prompt_resolver"]
            # Resolve the fix-bug.md template
            content, provenance = prompt_resolver_.resolve_template("fix-bug.md")
            
            if content is None:
                return {
                    "error": "Template fix-bug.md not found",
                    "tip": "Check prompt-packs installation with hub_prompts_status()",
                }
            
            return {
                "action": "fix_bug",
                "prompt_template": content,
                "provenance": provenance,
                "instructions": (
                    "Use the prompt template above to guide the conversation. "
                    "Ask the user about the bug, then create the bug intent file."
                ),
                "files_to_create": [
                    "context/intent/bug-[name].md",
                ],
                "tip": "Focus on understanding the bug before proposing a fix",
            }
            
        except Exception as e:
            return {
                "error": f"Error loading fix-bug prompt: {str(e)}",
            }
    
    @mcp.tool()
    def cm_create_decision(repo_root: Optional[str] = None) -> dict:
        """Start creating a technical decision (ADR).
        
        Returns a conversational guide for documenting decisions:
        1. What decision needs to be made?
        2. What is the context?
        3. What is the chosen approach?
        4. Why this approach? (rationale)
        5. What alternatives were considered?
        
        The AI agent uses this to ask questions and create the decision file.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to create decision in that project.
        
        Returns:
            Dictionary with prompt guide and instructions.
        
        Example usage in chat:
            User: "We decided to use PostgreSQL"
            AI: calls cm_create_decision() → asks about context, rationale, alternatives
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            # Get next decision number
            index = loader_.index
            existing_decisions = list(index["decisions"].keys())
            if existing_decisions:
                # Find highest number and increment
                max_num = max(int(d) for d in existing_decisions if d.isdigit())
                next_number = f"{max_num + 1:03d}"
            else:
                next_number = "001"
            
            return {
                "action": "create_decision",
                "next_decision_number": next_number,
                "questions_to_ask": [
                    "1. What decision needs to be made? (title)",
                    "2. What is the context? (situation, requirements, constraints)",
                    "3. What approach did you choose?",
                    "4. Why this approach? (rationale - reasons for choosing)",
                    "5. What alternatives did you consider? (and why not chosen)",
                    "6. What are the consequences? (positive and trade-offs)",
                ],
                "file_template": f"context/decisions/{next_number}-[slug].md",
                "adr_structure": {
                    "sections": [
                        "# Decision [number]: [title]",
                        "## Context",
                        "## Decision",
                        "## Rationale",
                        "## Alternatives Considered",
                        "## Consequences",
                        "## Related",
                        "## Status",
                    ],
                },
                "instructions": (
                    "Ask the questions above to gather information, then create "
                    f"the decision file at context/decisions/{next_number}-[slug].md"
                ),
                "tip": "Decisions should capture WHY, not just WHAT. The rationale is crucial.",
            }
            
        except Exception as e:
            return {
                "error": f"Error preparing decision creation: {str(e)}",
            }
    
    @mcp.tool()
    def cm_update_feature(feature_name: Optional[str] = None, repo_root: Optional[str] = None) -> dict:
        """Start updating an existing feature.
        
        Returns a conversational prompt that guides through:
        1. Which feature to update
        2. What is changing
        3. Why the change is needed
        4. Whether acceptance criteria change
        5. Whether a new technical decision is needed
        
        Args:
            feature_name: Optional - if provided, skips the "which feature" question.
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to update feature in that project.
        
        Returns:
            Dictionary with prompt template and current feature info.
        
        Example usage in chat:
            User: "Update the user-auth feature"
            AI: calls cm_update_feature("user-auth") → gets prompt → asks what's changing
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            prompt_resolver_ = comp["prompt_resolver"]
            loader_ = comp["loader"]
            # Resolve the update-feature.md template
            content, provenance = prompt_resolver_.resolve_template("update-feature.md")
            
            if content is None:
                return {
                    "error": "Template update-feature.md not found",
                    "tip": "Check prompt-packs installation with hub_prompts_status()",
                }
            
            # Get list of existing features
            index = loader_.index
            available_features = list(index["feature_intents"].keys())
            
            # If feature_name provided, validate it exists
            current_feature_content = None
            if feature_name:
                feature = index["feature_intents"].get(feature_name)
                if feature:
                    current_feature_content = feature.get("content", "")
                else:
                    return {
                        "error": f"Feature '{feature_name}' not found",
                        "available_features": available_features,
                        "tip": f"Did you mean one of these? Or use cm_add_feature() to create a new one.",
                    }
            
            return {
                "action": "update_feature",
                "prompt_template": content,
                "provenance": provenance,
                "available_features": available_features,
                "selected_feature": feature_name,
                "current_content": current_feature_content[:500] + "..." if current_feature_content and len(current_feature_content) > 500 else current_feature_content,
                "instructions": (
                    "Use the prompt template to guide the conversation. "
                    "Ask what is changing and why, then update the feature file."
                ),
                "key_principle": "Update the same file - Git preserves history. Don't create feature-v2.md.",
            }
            
        except Exception as e:
            return {
                "error": f"Error loading update-feature prompt: {str(e)}",
            }
    
    @mcp.tool()
    def cm_create_agent(repo_root: Optional[str] = None) -> dict:
        """Start creating a reusable execution agent.
        
        Returns a conversational prompt that guides through:
        1. Agent name
        2. What it does (purpose)
        3. Which context files it needs
        4. Execution steps
        5. Definition of Done
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to create agent in that project.
        
        Returns:
            Dictionary with prompt template and instructions.
        
        Example usage in chat:
            User: "Create an agent for API development"
            AI: calls cm_create_agent() → asks questions → creates agent file
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            prompt_resolver_ = comp["prompt_resolver"]
            loader_ = comp["loader"]
            # Resolve the create-agent.md template
            content, provenance = prompt_resolver_.resolve_template("create-agent.md")
            
            if content is None:
                return {
                    "error": "Template create-agent.md not found",
                    "tip": "Check prompt-packs installation with hub_prompts_status()",
                }
            
            # Get list of existing agents for reference
            index = loader_.index
            existing_agents = list(index["agents"].keys())
            
            return {
                "action": "create_agent",
                "prompt_template": content,
                "provenance": provenance,
                "existing_agents": existing_agents,
                "instructions": (
                    "Use the prompt template to guide the conversation. "
                    "Ask about agent purpose, context files needed, and execution steps."
                ),
                "file_template": "context/agents/agent-[name].md",
                "key_principle": "Agents should REFERENCE context, not duplicate it.",
                "tip": "Keep agents simple - they're just reusable prompts",
            }
            
        except Exception as e:
            return {
                "error": f"Error loading create-agent prompt: {str(e)}",
            }
    
    # ============================================
    # PROJECT SETUP TOOLS (Greenfield/Brownfield)
    # ============================================
    # These tools help users start with Context Mesh - creating new projects
    # or adding Context Mesh to existing projects.
    
    @mcp.tool()
    def cm_new_project(repo_root: Optional[str] = None) -> dict:
        """Start setting up a new project with Context Mesh.
        
        Returns a conversational prompt that guides through:
        1. Project name
        2. Project type (web app, API, CLI, etc.)
        3. What problem it solves
        4. Why it's important
        5. Tech stack (optional)
        6. Initial features (optional)
        
        The AI agent uses this prompt to ask questions and create the files.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to set up Context Mesh there.
        
        Returns:
            Dictionary with prompt template and instructions.
        
        Example usage in chat:
            User: "I want to start a new project"
            AI: calls cm_new_project() → gets prompt → asks questions → creates files
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            prompt_resolver_ = comp["prompt_resolver"]
            # Resolve the new-project.md template
            content, provenance = prompt_resolver_.resolve_template("new-project.md")
            
            if content is None:
                return {
                    "error": "Template new-project.md not found",
                    "tip": "Check prompt-packs installation with hub_prompts_status()",
                }
            
            return {
                "action": "new_project",
                "prompt_template": content,
                "provenance": provenance,
                "instructions": (
                    "Use the prompt template above to guide the conversation. "
                    "Ask the questions listed, then create ALL the context files "
                    "based on the user's answers."
                ),
                "files_to_create": [
                    "context/intent/project-intent.md",
                    "context/decisions/001-tech-stack.md (if tech stack provided)",
                    "context/evolution/changelog.md",
                    "context/.context-mesh-framework.md",
                    "AGENTS.md",
                    "context/intent/feature-*.md (if features provided)",
                ],
                "structure": [
                    "context/",
                    "├── .context-mesh-framework.md",
                    "├── intent/",
                    "│   └── project-intent.md",
                    "├── decisions/",
                    "├── knowledge/",
                    "│   ├── patterns/",
                    "│   └── anti-patterns/",
                    "├── agents/",
                    "└── evolution/",
                    "    └── changelog.md",
                    "AGENTS.md",
                ],
                "tip": "Ask questions one at a time. User can say 'skip' for optional questions.",
            }
            
        except Exception as e:
            return {
                "error": f"Error loading new-project prompt: {str(e)}",
            }
    
    @mcp.tool()
    def cm_existing_project(repo_root: Optional[str] = None) -> dict:
        """Start adding Context Mesh to an existing project (brownfield).
        
        Returns a conversational prompt that guides through:
        1. Analyzing existing code structure
        2. Extracting decisions from code
        3. Documenting existing features
        4. Creating context/ structure
        
        The AI agent uses this prompt to analyze the code and create context.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to add Context Mesh to that project.
        
        Returns:
            Dictionary with prompt template and instructions.
        
        Example usage in chat:
            User: "Add Context Mesh to my existing project"
            AI: calls cm_existing_project() → analyzes code → asks to confirm → creates files
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            prompt_resolver_ = comp["prompt_resolver"]
            # Resolve the existing-project.md template
            content, provenance = prompt_resolver_.resolve_template("existing-project.md")
            
            if content is None:
                return {
                    "error": "Template existing-project.md not found",
                    "tip": "Check prompt-packs installation with hub_prompts_status()",
                }
            
            return {
                "action": "existing_project",
                "prompt_template": content,
                "provenance": provenance,
                "instructions": (
                    "Use the prompt template to guide the conversation. "
                    "First analyze the codebase using brownfield_scan(), then "
                    "ask the user to confirm findings before creating files."
                ),
                "analysis_tools": [
                    "brownfield_scan() - Analyze project structure",
                    "brownfield_slice() - Identify modules/features",
                    "brownfield_extract() - Extract context artifacts",
                ],
                "files_to_create": [
                    "context/intent/project-intent.md (from analysis)",
                    "context/decisions/001-tech-stack.md (from dependencies)",
                    "context/intent/feature-*.md (from modules found)",
                    "context/knowledge/patterns/*.md (if patterns found)",
                    "context/evolution/changelog.md",
                    "AGENTS.md",
                ],
                "tip": "Always show analysis results and ask for confirmation before creating files",
            }
            
        except Exception as e:
            return {
                "error": f"Error loading existing-project prompt: {str(e)}",
            }
    
    @mcp.tool()
    def cm_init(repo_root: Optional[str] = None) -> dict:
        """Initialize Context Mesh in current directory.
        
        Quick initialization - creates minimal structure.
        Use cm_new_project() for full setup with details.
        
        Args:
            repo_root: Path to the repository root. If not provided, uses server default.
                       Pass the current project path to initialize Context Mesh there.
        
        Returns:
            Dictionary with minimal files to create.
        """
        try:
            comp = _get_components_for_repo(repo_root, default_components)
            loader_ = comp["loader"]
            from datetime import date
            today = date.today().isoformat()
            
            # Get project name from current directory
            project_name = loader_.repo_root.name if loader_.repo_root else "my-project"
            
            files_to_create = {
                "context/intent/project-intent.md": f"""# Project Intent: {project_name}

## What

_Describe what this project does_

## Why

_Explain why this project matters_

## Status

- **Created**: {today}
- **Status**: Draft
""",
                "context/evolution/changelog.md": f"""# Changelog

## [{today}] - Initialized

### Added
- Context Mesh initialized
""",
                "context/decisions/.gitkeep": "",
                "context/knowledge/patterns/.gitkeep": "",
                "context/knowledge/anti-patterns/.gitkeep": "",
                "context/agents/.gitkeep": "",
                "AGENTS.md": f"""# AGENTS.md

> Load @context/ files before implementing.

## Workflow
Intent → Build → Learn

## Files to Load
- @context/intent/project-intent.md
- @context/decisions/*.md
""",
            }
            
            return {
                "success": True,
                "action": "init",
                "files_to_create": files_to_create,
                "file_count": len(files_to_create),
                "next_steps": [
                    "1. Create these files",
                    "2. Edit project-intent.md with your project details",
                    "3. Use cm_add_feature() to add features",
                ],
            }
            
        except Exception as e:
            return {
                "error": f"Error initializing: {str(e)}",
            }
