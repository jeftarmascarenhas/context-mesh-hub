"""Markdown parsing utilities.

Centralized markdown parsing and extraction to avoid duplication.
"""

import re
from typing import List, Optional, Set


class MarkdownParser:
    """Parser for Context Mesh markdown files.
    
    Provides methods to extract common sections and metadata from
    feature intents, decisions, and other context artifacts.
    """
    
    @staticmethod
    def extract_title(content: str) -> str:
        """Extract title from first heading.
        
        Args:
            content: Markdown content.
            
        Returns:
            Title text without # prefix, or empty string if not found.
            
        Example:
            >>> MarkdownParser.extract_title("# Feature F001: Auth\\n\\nDescription")
            'Feature F001: Auth'
        """
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return ""
    
    @staticmethod
    def extract_status(content: str) -> str:
        """Extract status from Status field.
        
        Looks for patterns like:
        - **Status**: Active
        - Status: Draft
        
        Args:
            content: Markdown content.
            
        Returns:
            Status text, or "Unknown" if not found.
        """
        status_patterns = [
            (r"\*\*Status\*\*:\s*(\w+)", "bold"),
            (r"Status:\s*(\w+)", "plain"),
            (r"-\s+\*\*Status\*\*:\s*(\w+)", "list_bold"),
        ]
        
        for pattern, _ in status_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    @staticmethod
    def extract_section(content: str, section_name: str) -> str:
        """Extract content of a section by heading.
        
        Args:
            content: Markdown content.
            section_name: Section heading text (without ##).
            
        Returns:
            Section content, or empty string if not found.
            
        Example:
            >>> content = "## What\\n\\nAuth system\\n\\n## Why\\n\\nSecurity"
            >>> MarkdownParser.extract_section(content, "What")
            'Auth system'
        """
        # Match ## Section or ### Section
        pattern = rf"###+\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##|$)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    @staticmethod
    def extract_list_items(content: str, section_name: str) -> List[str]:
        """Extract list items from a section.
        
        Args:
            content: Markdown content.
            section_name: Section heading text.
            
        Returns:
            List of items (without bullets).
            
        Example:
            >>> content = "## Acceptance Criteria\\n\\n- [ ] AC1\\n- [x] AC2"
            >>> MarkdownParser.extract_list_items(content, "Acceptance Criteria")
            ['AC1', 'AC2']
        """
        section_content = MarkdownParser.extract_section(content, section_name)
        if not section_content:
            return []
        
        items = []
        # Match list items: - item, * item, - [ ] item, - [x] item
        list_pattern = r"^\s*[-*]\s*(?:\[[x\s]\]\s*)?(.+)$"
        
        for line in section_content.split("\n"):
            match = re.match(list_pattern, line.strip())
            if match:
                items.append(match.group(1).strip())
        
        return items
    
    @staticmethod
    def extract_decision_links(content: str) -> Set[str]:
        """Extract decision references from content.
        
        Looks for patterns like: D001, D042, decision-001, etc.
        
        Args:
            content: Markdown content.
            
        Returns:
            Set of decision identifiers.
            
        Example:
            >>> content = "See D001 and D042 for details"
            >>> MarkdownParser.extract_decision_links(content)
            {'D001', 'D042'}
        """
        decisions = set()
        
        # Pattern: D001, D042, etc.
        pattern = r"\bD\d{3,}\b"
        matches = re.findall(pattern, content)
        decisions.update(matches)
        
        # Pattern: decision-001, etc.
        pattern2 = r"\bdecision-(\d{3,})\b"
        matches2 = re.findall(pattern2, content, re.IGNORECASE)
        decisions.update(f"D{num}" for num in matches2)
        
        return decisions
    
    @staticmethod
    def extract_feature_links(content: str) -> Set[str]:
        """Extract feature references from content.
        
        Looks for patterns like: F001, F042, feature-auth, etc.
        
        Args:
            content: Markdown content.
            
        Returns:
            Set of feature identifiers.
        """
        features = set()
        
        # Pattern: F001, F042, etc.
        pattern = r"\bF\d{3,}\b"
        matches = re.findall(pattern, content)
        features.update(matches)
        
        return features
    
    @staticmethod
    def extract_code_blocks(content: str, language: Optional[str] = None) -> List[str]:
        """Extract code blocks from markdown.
        
        Args:
            content: Markdown content.
            language: Optional language filter (e.g., "python", "bash").
            
        Returns:
            List of code block contents.
        """
        code_blocks = []
        
        if language:
            pattern = rf"```{language}\n(.*?)```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)```"
        
        matches = re.findall(pattern, content, re.DOTALL)
        code_blocks.extend(match.strip() for match in matches)
        
        return code_blocks
    
    @staticmethod
    def extract_metadata(content: str) -> dict:
        """Extract metadata fields from content.
        
        Looks for patterns like:
        - **Date**: 2026-03-03
        - **Created**: 2026-03-03
        
        Args:
            content: Markdown content.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        metadata = {}
        
        # Pattern: **Key**: Value or - **Key**: Value
        pattern = r"(?:^|\n)\s*-?\s*\*\*([^*]+)\*\*:\s*(.+)"
        matches = re.findall(pattern, content)
        
        for key, value in matches:
            metadata[key.strip()] = value.strip()
        
        return metadata
