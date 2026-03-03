"""Prompt template resolver for Context Mesh Hub.

Implements Decision 010: Prompt Pack Resolution and Update Model.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import os


class PromptResolver:
    """Resolves prompt templates using the resolution order from Decision 010.
    
    Resolution order:
    1. Repo override: <repoRoot>/.context-mesh/prompts/<template>.md
    2. Pinned cached pack: ~/.context-mesh-hub/prompt-packs/<pack>/<version>/<template>.md
    3. Bundled fallback: internal bundled pack
    """
    
    # Canonical template names
    TEMPLATE_NAMES = {
        "new-project.md",
        "existing-project.md",
        "add-feature.md",
        "add-decision.md",
        "update-feature.md",
        "fix-bug.md",
        "create-agent.md",
        "learn-update.md",
    }
    
    def __init__(self, repo_root: Path):
        """Initialize resolver with repository root.
        
        Args:
            repo_root: Repository root path.
        """
        self.repo_root = repo_root
        self.repo_override_dir = repo_root / ".context-mesh" / "prompts"
        self.cache_dir = Path.home() / ".context-mesh-hub" / "prompt-packs"
        
        # Bundled fallback location (relative to hub-core package)
        # This will be resolved relative to the package location
        self._bundled_base = None
    
    def _get_bundled_base(self) -> Path:
        """Get the base path for bundled prompt packs.
        
        Returns:
            Path to bundled prompt packs directory.
        """
        if self._bundled_base is None:
            # Resolve relative to this module's location
            module_dir = Path(__file__).parent.parent.parent
            self._bundled_base = module_dir / "prompt-packs"
        return self._bundled_base
    
    def _read_manifest(self) -> Optional[Dict]:
        """Read hub-manifest.json from repository.
        
        Returns:
            Manifest dict or None if not found.
        """
        manifest_path = self.repo_root / "context" / "hub-manifest.json"
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _get_pinned_pack(self) -> Optional[Tuple[str, str, str]]:
        """Get pinned pack info from manifest.
        
        Returns:
            Tuple of (pack_name, version, source) or None.
        """
        manifest = self._read_manifest()
        if not manifest or "promptPack" not in manifest:
            return None
        
        pack_info = manifest["promptPack"]
        return (
            pack_info.get("name"),
            pack_info.get("version"),
            pack_info.get("source", "bundled"),
        )
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of template content.
        
        Args:
            content: Template content.
            
        Returns:
            Hex digest of hash.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def _read_file(self, path: Path) -> Optional[str]:
        """Safely read a file.
        
        Args:
            path: File path.
            
        Returns:
            File content or None if not found/invalid.
        """
        try:
            if path.exists() and path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except (IOError, UnicodeDecodeError):
            pass
        return None
    
    def resolve_template(
        self, template_name: str
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """Resolve a template using the resolution order.
        
        Args:
            template_name: Template filename (e.g., "add-feature.md").
            
        Returns:
            Tuple of (content, provenance_dict).
            content is None if template not found.
            provenance_dict contains: packName, packVersion, templateName,
            templateHash, resolutionSource.
        """
        if template_name not in self.TEMPLATE_NAMES:
            return None, None
        
        provenance = {
            "templateName": template_name,
            "packName": None,
            "packVersion": None,
            "templateHash": None,
            "resolutionSource": None,
        }
        
        # 1. Try repo override (highest priority)
        repo_override_path = self.repo_override_dir / template_name
        content = self._read_file(repo_override_path)
        if content:
            provenance["resolutionSource"] = "repoOverride"
            provenance["templateHash"] = self._compute_hash(content)
            return content, provenance
        
        # 2. Try pinned cached pack
        pinned = self._get_pinned_pack()
        if pinned:
            pack_name, version, source = pinned
            if source == "cached" or source is None:
                cached_path = (
                    self.cache_dir / pack_name / version / template_name
                )
                content = self._read_file(cached_path)
                if content:
                    provenance["packName"] = pack_name
                    provenance["packVersion"] = version
                    provenance["resolutionSource"] = "cached"
                    provenance["templateHash"] = self._compute_hash(content)
                    return content, provenance
        
        # 3. Try bundled fallback
        bundled_base = self._get_bundled_base()
        
        # If we have a pinned pack, try that version first
        if pinned:
            pack_name, version, _ = pinned
            bundled_path = bundled_base / pack_name / version / template_name
            content = self._read_file(bundled_path)
            if content:
                provenance["packName"] = pack_name
                provenance["packVersion"] = version
                provenance["resolutionSource"] = "bundled"
                provenance["templateHash"] = self._compute_hash(content)
                return content, provenance
        
        # Default bundled pack (context-mesh-core/1.0.0)
        default_bundled_path = (
            bundled_base / "context-mesh-core" / "1.0.0" / template_name
        )
        content = self._read_file(default_bundled_path)
        if content:
            provenance["packName"] = "context-mesh-core"
            provenance["packVersion"] = "1.0.0"
            provenance["resolutionSource"] = "bundled"
            provenance["templateHash"] = self._compute_hash(content)
            return content, provenance
        
        # Template not found in any source
        return None, None
