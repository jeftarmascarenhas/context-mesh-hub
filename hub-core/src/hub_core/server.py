"""MCP server entry point for Hub Core.

Refactored with Dependency Injection (Fase 5).
All dependencies are instantiated here and injected into services and tools.
"""

import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

# Infrastructure layer
from .loader import ContextLoader
from .validator import ContextValidator
from .bundler import ContextBundler
from .infrastructure.parsers.markdown_parser import MarkdownParser
from .infrastructure.parsers.extractor import (
    FeatureExtractor,
    DecisionExtractor,
    BuildPlanExtractor,
)
from .infrastructure.persistence.file_store import FileStore
from .infrastructure.persistence.plan_repository import PlanRepository
from .infrastructure.persistence.proposal_repository import ProposalRepository
from .infrastructure.scanner.repo_scanner import RepositoryScanner
from .infrastructure.scanner.slice_generator import SliceGenerator
from .infrastructure.scanner.context_extractor import ContextExtractor

# Domain services
from .domain.services.intent_service import IntentService
from .domain.services.build_service import BuildService
from .domain.services.analysis_service import AnalysisService
from .domain.services.learn_service import LearnService

# MCP tools
from .mcp.tools.cm_init import register_cm_init
from .mcp.tools.cm_intent import register_cm_intent
from .mcp.tools.cm_agent import register_cm_agent
from .mcp.tools.cm_analyze import register_cm_analyze
from .mcp.tools.cm_build import register_cm_build
from .mcp.tools.cm_learn import register_cm_learn
from .mcp.tools.cm_validate import register_cm_validate
from .mcp.tools.cm_status import register_cm_status
from .mcp.tools.cm_help import register_cm_help

# Additional components (prompt packs, etc.)
from .prompt_resolver import PromptResolver
from .prompt_pack_manager import PromptPackManager


def create_server(repo_root: Optional[Path] = None) -> FastMCP:
    """Create and configure the Hub Core MCP server with DI.
    
    This function instantiates all dependencies and injects them into
    services and tools following the 3-layer architecture:
    - Infrastructure: Parsers, persistence, scanners
    - Domain: Business logic services
    - MCP: Thin tool wrappers
    
    Args:
        repo_root: Optional repository root path. Auto-detects if None.
    
    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP("Hub Core")
    
    # Use provided repo_root or current directory
    effective_repo_root = repo_root or Path.cwd()
    
    # ========================================================================
    # INFRASTRUCTURE LAYER - Instantiate all I/O components
    # ========================================================================
    
    # Context loader and validator
    loader = ContextLoader(effective_repo_root)
    validator = ContextValidator(loader)
    
    # Load context index (returns empty if no context/)
    try:
        loader.load()
    except Exception:
        # Gracefully handle missing context (greenfield projects)
        pass
    
    # Bundler (only if context exists)
    bundler = None
    if loader.context_dir.exists():
        bundler = ContextBundler(loader)
    
    # Parsers
    parser = MarkdownParser()
    feature_extractor = FeatureExtractor(parser)
    decision_extractor = DecisionExtractor(parser)
    build_plan_extractor = BuildPlanExtractor(parser)
    
    # Persistence layer (file-based)
    persistence_dir = effective_repo_root / ".context-mesh"
    persistence_dir.mkdir(exist_ok=True)
    
    file_store = FileStore(persistence_dir)
    plan_repository = PlanRepository(file_store)
    proposal_repository = ProposalRepository(file_store)
    
    # Scanner modules (brownfield analysis)
    scanner = RepositoryScanner(effective_repo_root)
    slice_generator = SliceGenerator(scanner)
    context_extractor = ContextExtractor(scanner)
    
    # Prompt pack resolution
    prompt_resolver = PromptResolver(effective_repo_root)
    pack_manager = PromptPackManager(effective_repo_root)
    
    # ========================================================================
    # DOMAIN LAYER - Instantiate all services with DI
    # ========================================================================
    
    intent_service = IntentService(
        loader=loader,
        parser=parser,
    )
    
    build_service = None
    if bundler:  # Only create if context exists
        build_service = BuildService(
            loader=loader,
            bundler=bundler,
            plan_repository=plan_repository,
            parser=parser,
            extractor=build_plan_extractor,
        )
    
    analysis_service = AnalysisService(
        scanner=scanner,
        slice_generator=slice_generator,
        context_extractor=context_extractor,
    )
    
    learn_service = LearnService(
        loader=loader,
        proposal_repository=proposal_repository,
        parser=parser,
    )
    
    # ========================================================================
    # MCP LAYER - Register all 8 tools with injected dependencies
    # ========================================================================
    
    register_cm_init(
        mcp=mcp,
        loader=loader,
        validator=validator,
        parser=parser,
    )
    
    register_cm_intent(
        mcp=mcp,
        intent_service=intent_service,
    )
    
    register_cm_agent(
        mcp=mcp,
        intent_service=intent_service,
    )
    
    register_cm_analyze(
        mcp=mcp,
        analysis_service=analysis_service,
    )
    
    if build_service:
        register_cm_build(
            mcp=mcp,
            build_service=build_service,
            bundler=bundler,
        )
    
    register_cm_learn(
        mcp=mcp,
        learn_service=learn_service,
    )
    
    register_cm_validate(
        mcp=mcp,
        validator=validator,
        loader=loader,
    )
    
    register_cm_status(
        mcp=mcp,
        loader=loader,
        validator=validator,
        plan_repository=plan_repository,
        proposal_repository=proposal_repository,
    )
    
    register_cm_help(mcp=mcp)
    
    return mcp


def main():
    """Main entry point for the MCP server."""
    import os
    
    # Allow repo root to be passed as command-line argument
    repo_root = None
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1]).resolve()
    else:
        # Try to auto-detect from environment or cwd
        # CONTEXT_MESH_REPO_ROOT env var takes priority
        env_root = os.environ.get("CONTEXT_MESH_REPO_ROOT")
        if env_root:
            repo_root = Path(env_root).resolve()
        else:
            # Use current working directory (set by Cursor to workspace)
            cwd = Path.cwd()
            if (cwd / "context").exists():
                repo_root = cwd
    
    server = create_server(repo_root)
    
    # Run the server in stdio mode (for MCP clients like Cursor)
    # show_banner=False to avoid rich UI when running as MCP server
    server.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
