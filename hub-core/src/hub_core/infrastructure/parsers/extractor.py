"""Context extraction utilities.

High-level extractors for specific context artifact types.
"""

from typing import List, Set

from .markdown_parser import MarkdownParser


class FeatureExtractor:
    """Extract structured data from feature intent files."""
    
    def __init__(self, parser: MarkdownParser = None):
        self.parser = parser or MarkdownParser()
    
    def extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria from feature intent."""
        return self.parser.extract_list_items(content, "Acceptance Criteria")
    
    def extract_what(self, content: str) -> str:
        """Extract 'What' section from feature intent."""
        return self.parser.extract_section(content, "What")
    
    def extract_why(self, content: str) -> str:
        """Extract 'Why' section from feature intent."""
        return self.parser.extract_section(content, "Why")
    
    def extract_related_decisions(self, content: str) -> Set[str]:
        """Extract related decisions from feature intent."""
        # Check Related Decisions section
        section = self.parser.extract_section(content, "Related Decisions")
        return self.parser.extract_decision_links(section + content)


class DecisionExtractor:
    """Extract structured data from decision files."""
    
    def __init__(self, parser: MarkdownParser = None):
        self.parser = parser or MarkdownParser()
    
    def extract_context(self, content: str) -> str:
        """Extract 'Context' section from decision."""
        return self.parser.extract_section(content, "Context")
    
    def extract_decision(self, content: str) -> str:
        """Extract 'Decision' section."""
        return self.parser.extract_section(content, "Decision")
    
    def extract_rationale(self, content: str) -> str:
        """Extract 'Rationale' section."""
        return self.parser.extract_section(content, "Rationale")
    
    def extract_alternatives(self, content: str) -> List[str]:
        """Extract alternatives considered."""
        return self.parser.extract_list_items(content, "Alternatives Considered")
    
    def extract_consequences(self, content: str) -> dict:
        """Extract consequences (positive and trade-offs)."""
        consequences = {}
        
        # Extract Positive section
        positive_section = self.parser.extract_section(content, "Positive")
        if positive_section:
            consequences["positive"] = self.parser.extract_list_items(
                f"## Positive\n{positive_section}", "Positive"
            )
        
        # Extract Trade-offs section
        tradeoffs_section = self.parser.extract_section(content, "Trade-offs")
        if tradeoffs_section:
            consequences["tradeoffs"] = self.parser.extract_list_items(
                f"## Trade-offs\n{tradeoffs_section}", "Trade-offs"
            )
        
        return consequences


class BuildPlanExtractor:
    """Extract structured data for build planning."""
    
    def __init__(self, parser: MarkdownParser = None):
        self.parser = parser or MarkdownParser()
    
    def extract_constraints(self, content: str) -> List[str]:
        """Extract constraints from feature intent."""
        return self.parser.extract_list_items(content, "Constraints")
    
    def extract_non_goals(self, content: str) -> List[str]:
        """Extract non-goals."""
        return self.parser.extract_list_items(content, "Non-Goals")
    
    def extract_risks(self, content: str) -> List[str]:
        """Extract risks."""
        return self.parser.extract_list_items(content, "Risks")
    
    def extract_assumptions(self, content: str) -> List[str]:
        """Extract assumptions."""
        return self.parser.extract_list_items(content, "Assumptions")
    
    def extract_implementation_approach(self, content: str) -> str:
        """Extract implementation approach section."""
        # Try various section names
        for section_name in ["Implementation", "Approach", "Implementation Approach"]:
            approach = self.parser.extract_section(content, section_name)
            if approach:
                return approach
        return ""
