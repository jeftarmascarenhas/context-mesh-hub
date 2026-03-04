"""MCP Tool: cm_analyze - Brownfield analysis.

Tool 4 of 8: Scan, slice, extract, and report for brownfield codebases.
"""

from typing import Optional, Dict, Any

from fastmcp import FastMCP

from ...domain.services.analysis_service import AnalysisService
from ..decorators import handle_mcp_errors


def register_cm_analyze(
    mcp: FastMCP,
    analysis_service: AnalysisService,
):
    """Register cm_analyze tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        analysis_service: AnalysisService instance
    """
    
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
    )
    @handle_mcp_errors
    def cm_analyze(
        action: str,
        target: Optional[str] = None,
        strategy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze existing codebase for brownfield Context Mesh adoption.
        
        Consolidates brownfield analysis into a single tool.
        
        Args:
            action: Action to perform:
                - "scan": Analyze repository structure
                - "slice": Generate repository slices for analysis
                - "extract": Extract proposed context artifacts from a slice
                - "report": Generate comprehensive analysis report
                - "impact": Analyze impact of changes
                - "dependencies": Analyze project dependencies
            target: Target for the action:
                - For "scan": path to scan (defaults to repo root)
                - For "extract": slice ID
                - For "report": slice ID filter (optional)
            strategy: Strategy for slice generation:
                - "directory": By directory structure
                - "module": By detected modules
                - "language": By programming language
        
        Returns:
            Dictionary with analysis results based on action
        
        Examples:
            # Scan repository
            cm_analyze(action="scan")
            
            # Generate slices by module
            cm_analyze(action="slice", strategy="module")
            
            # Extract context from a slice
            cm_analyze(action="extract", target="slice-src")
            
            # Generate full report
            cm_analyze(action="report")
        """
        valid_actions = ["scan", "slice", "extract", "report", "impact", "dependencies"]
        if action not in valid_actions:
            return {"error": f"Invalid action: {action}", "valid_actions": valid_actions}
        
        # ====================================================================
        # ACTION: SCAN
        # ====================================================================
        if action == "scan":
            analysis = analysis_service.scan()
            return {
                "action": "scan",
                "analysis": {
                    "languages": sorted(list(analysis.languages)),
                    "frameworks": sorted(list(analysis.frameworks)),
                    "entry_points": analysis.entry_points,
                    "build_tools": analysis.build_tools,
                    "has_tests": analysis.has_tests,
                    "file_count": analysis.file_count,
                    "directory_count": analysis.directory_count,
                },
                "next_step": "Use cm_analyze(action='slice', strategy='directory') to generate slices",
            }
        
        # ====================================================================
        # ACTION: SLICE
        # ====================================================================
        elif action == "slice":
            if not strategy:
                return {
                    "error": "Strategy required for slice action",
                    "valid_strategies": ["directory", "module", "language"],
                }
            
            slices = analysis_service.generate_slices(strategy)
            return {
                "action": "slice",
                "strategy": strategy,
                "slices": [
                    {
                        "slice_id": s.slice_id,
                        "name": s.name,
                        "path": str(s.path),
                        "file_count": len(s.file_paths),
                    }
                    for s in slices
                ],
                "total": len(slices),
                "next_step": "Use cm_analyze(action='extract', target='<slice_id>') to extract artifacts",
            }
        
        # ====================================================================
        # ACTION: EXTRACT
        # ====================================================================
        elif action == "extract":
            if not target:
                return {"error": "Target (slice_id) required for extract action"}
            
            artifacts = analysis_service.extract_artifacts(target)
            return {
                "action": "extract",
                "slice_id": target,
                "artifacts": [
                    {
                        "type": a.artifact_type,
                        "title": a.title,
                        "confidence": a.confidence.value,
                        "evidence_count": len(a.evidence),
                    }
                    for a in artifacts
                ],
                "total": len(artifacts),
            }
        
        # ====================================================================
        # ACTION: REPORT
        # ====================================================================
        elif action == "report":
            report = analysis_service.generate_report(slice_filter=target)
            return {
                "action": "report",
                "report": report,
            }
        
        # ====================================================================
        # ACTION: DEPENDENCIES
        # ====================================================================
        elif action == "dependencies":
            deps = analysis_service.analyze_dependencies()
            return {
                "action": "dependencies",
                "dependencies": deps,
            }
        
        # ====================================================================
        # ACTION: IMPACT (placeholder)
        # ====================================================================
        elif action == "impact":
            return {
                "error": "Impact analysis requires changed_files parameter",
                "tip": "Use after making changes to analyze impact on slices",
            }
