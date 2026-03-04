"""Shared pytest fixtures for hub-core tests.

Provides common fixtures for testing domain services, infrastructure, and MCP tools.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from hub_core.loader import ContextLoader
from hub_core.bundler import ContextBundler
from hub_core.infrastructure.parsers.markdown_parser import MarkdownParser
from hub_core.infrastructure.parsers.extractor import BuildPlanExtractor
from hub_core.infrastructure.persistence.file_store import FileStore
from hub_core.infrastructure.persistence.plan_repository import PlanRepository
from hub_core.infrastructure.persistence.proposal_repository import ProposalRepository
from hub_core.infrastructure.scanner.repo_scanner import RepositoryScanner
from hub_core.infrastructure.scanner.slice_generator import SliceGenerator
from hub_core.infrastructure.scanner.context_extractor import ContextExtractor

from hub_core.domain.services.intent_service import IntentService
from hub_core.domain.services.build_service import BuildService
from hub_core.domain.services.analysis_service import AnalysisService
from hub_core.domain.services.learn_service import LearnService


# ============================================================================
# REPO ROOT FIXTURE
# ============================================================================

@pytest.fixture(scope="session")
def repo_root():
    """Get repository root path."""
    # Assuming tests are in hub-core/tests, repo is 2 levels up
    return Path(__file__).parent.parent.parent


# ============================================================================
# LOADER FIXTURES
# ============================================================================

@pytest.fixture
def context_loader(repo_root):
    """Create ContextLoader instance."""
    loader = ContextLoader(repo_root)
    loader.load()
    return loader


@pytest.fixture
def context_bundler(context_loader):
    """Create ContextBundler instance."""
    return ContextBundler(context_loader)


# ============================================================================
# PARSER FIXTURES
# ============================================================================

@pytest.fixture
def markdown_parser():
    """Create MarkdownParser instance."""
    return MarkdownParser()


@pytest.fixture
def build_plan_extractor():
    """Create BuildPlanExtractor instance."""
    return BuildPlanExtractor()


# ============================================================================
# PERSISTENCE FIXTURES
# ============================================================================

@pytest.fixture
def temp_file_store():
    """Create temporary FileStore for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield FileStore(Path(tmp_dir))


@pytest.fixture
def plan_repository(temp_file_store):
    """Create PlanRepository with temp storage."""
    return PlanRepository(temp_file_store)


@pytest.fixture
def proposal_repository(temp_file_store):
    """Create ProposalRepository with temp storage."""
    return ProposalRepository(temp_file_store)


# ============================================================================
# SCANNER FIXTURES
# ============================================================================

@pytest.fixture
def repo_scanner(repo_root):
    """Create RepositoryScanner instance."""
    return RepositoryScanner(repo_root)


@pytest.fixture
def slice_generator(repo_root):
    """Create SliceGenerator instance."""
    return SliceGenerator(repo_root)


@pytest.fixture
def context_extractor(context_loader):
    """Create ContextExtractor instance."""
    return ContextExtractor(context_loader)


# ============================================================================
# SERVICE FIXTURES
# ============================================================================

@pytest.fixture
def intent_service(context_loader, markdown_parser):
    """Create IntentService instance."""
    return IntentService(context_loader, markdown_parser)


@pytest.fixture
def build_service(
    context_loader,
    context_bundler,
    plan_repository,
    markdown_parser,
    build_plan_extractor
):
    """Create BuildService instance."""
    return BuildService(
        context_loader,
        context_bundler,
        plan_repository,
        markdown_parser,
        build_plan_extractor
    )


@pytest.fixture
def analysis_service(repo_scanner, slice_generator, context_extractor):
    """Create AnalysisService instance."""
    return AnalysisService(repo_scanner, slice_generator, context_extractor)


@pytest.fixture
def learn_service(context_loader, proposal_repository, markdown_parser):
    """Create LearnService instance."""
    return LearnService(context_loader, proposal_repository, markdown_parser)


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_feature_content():
    """Sample valid feature content."""
    return """# Feature F999: Test Feature

## What

A test feature for unit testing.

## Why

To validate feature creation and parsing.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Related Decisions

- D001

## Status

- **Created**: 2026-03-04
- **Status**: Draft
"""


@pytest.fixture
def sample_decision_content():
    """Sample valid decision content."""
    return """# Decision D999: Test Decision

## Context

Need to test decision creation.

## Decision

Use test-driven development for all new features.

## Rationale

TDD improves code quality and maintainability.

## Alternatives Considered

- **Manual testing**: Too slow and error-prone
- **No testing**: Unacceptable risk

## Consequences

### Positive
- Higher code quality
- Better test coverage
- Easier refactoring

### Trade-offs
- Slightly slower initial development
- Learning curve for new developers

## Related

- Features: F001, F002
- Decisions: D001

## Status

- **Date**: 2026-03-04
- **Status**: Accepted
"""


@pytest.fixture
def sample_markdown_with_sections():
    """Sample markdown content with multiple sections."""
    return """# Title

## What

This is the what section.

## Why

This is the why section.

## How

This is the how section.

## Acceptance Criteria

- [ ] AC1
- [x] AC2
- AC3

## Related Decisions

See D001 and D042 for details.

## Status

- **Created**: 2026-03-04
- **Status**: Active
"""
