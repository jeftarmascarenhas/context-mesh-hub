"""Prompt pack manager for installing, using, and verifying packs.

Implements Decision 010: Prompt Pack Resolution and Update Model.
"""

import hashlib
import json
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import urlopen
import tempfile


class PromptPackManager:
    """Manages prompt pack installation, pinning, and verification."""
    
    def __init__(self, repo_root: Path):
        """Initialize manager with repository root.
        
        Args:
            repo_root: Repository root path.
        """
        self.repo_root = repo_root
        self.cache_dir = Path.home() / ".context-mesh-hub" / "prompt-packs"
        self.manifest_path = repo_root / "context" / "hub-manifest.json"
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _read_manifest(self) -> Dict:
        """Read hub-manifest.json.
        
        Returns:
            Manifest dict (empty if not found).
        """
        if not self.manifest_path.exists():
            return {}
        
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _write_manifest(self, manifest: Dict) -> None:
        """Write hub-manifest.json.
        
        Args:
            manifest: Manifest dict to write.
        """
        # Ensure context directory exists
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def status(self) -> Dict:
        """Get current prompt pack status.
        
        Returns:
            Dict with current pack info, available cached versions, and bundled version.
        """
        manifest = self._read_manifest()
        pack_info = manifest.get("promptPack", {})
        
        current_pack = pack_info.get("name")
        current_version = pack_info.get("version")
        current_source = pack_info.get("source", "bundled")
        
        # List cached versions
        cached_versions = []
        if current_pack:
            pack_cache_dir = self.cache_dir / current_pack
            if pack_cache_dir.exists():
                for version_dir in pack_cache_dir.iterdir():
                    if version_dir.is_dir():
                        cached_versions.append(version_dir.name)
                cached_versions.sort(reverse=True)
        
        return {
            "current": {
                "packName": current_pack,
                "version": current_version,
                "source": current_source,
            },
            "cachedVersions": cached_versions,
            "bundledVersion": "1.0.0",  # Default bundled version
        }
    
    def install(
        self, pack_name: str, version: str, url: Optional[str] = None
    ) -> Dict:
        """Install a prompt pack from URL.
        
        Args:
            pack_name: Pack name (e.g., "context-mesh-core").
            version: Pack version (e.g., "1.10.0").
            url: Download URL. If None, constructs GitHub release URL.
            
        Returns:
            Dict with success status and message.
        """
        if url is None:
            # Default to GitHub release pattern
            url = (
                f"https://github.com/jeftarmascarenhas/context-mesh/releases/"
                f"download/v{version}/{pack_name}-{version}.zip"
            )
        
        target_dir = self.cache_dir / pack_name / version
        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)
            
            try:
                with urlopen(url) as response:
                    shutil.copyfileobj(response, open(tmp_path, "wb"))
                
                # Extract based on file extension
                if url.endswith(".zip"):
                    with zipfile.ZipFile(tmp_path, "r") as zip_ref:
                        # Extract to temp directory first
                        with tempfile.TemporaryDirectory() as extract_dir:
                            zip_ref.extractall(extract_dir)
                            extract_path = Path(extract_dir)
                            
                            # Find the pack directory structure
                            # Expected: <packName>/<version>/*.md or just *.md
                            pack_dir = None
                            if (extract_path / pack_name / version).exists():
                                pack_dir = extract_path / pack_name / version
                            elif (extract_path / pack_name).exists():
                                pack_dir = extract_path / pack_name
                            else:
                                # Try to find any .md files
                                md_files = list(extract_path.rglob("*.md"))
                                if md_files:
                                    pack_dir = extract_path
                            
                            if pack_dir:
                                # Copy .md files to target
                                for md_file in pack_dir.rglob("*.md"):
                                    target_file = target_dir / md_file.name
                                    shutil.copy2(md_file, target_file)
                            else:
                                return {
                                    "error": "Could not find pack structure in archive",
                                }
                
                elif url.endswith((".tar.gz", ".tgz")):
                    with tarfile.open(tmp_path, "r:gz") as tar_ref:
                        # Extract to temp directory
                        with tempfile.TemporaryDirectory() as extract_dir:
                            tar_ref.extractall(extract_dir)
                            extract_path = Path(extract_dir)
                            
                            # Similar logic as zip
                            pack_dir = None
                            if (extract_path / pack_name / version).exists():
                                pack_dir = extract_path / pack_name / version
                            elif (extract_path / pack_name).exists():
                                pack_dir = extract_path / pack_name
                            else:
                                md_files = list(extract_path.rglob("*.md"))
                                if md_files:
                                    pack_dir = extract_path
                            
                            if pack_dir:
                                for md_file in pack_dir.rglob("*.md"):
                                    target_file = target_dir / md_file.name
                                    shutil.copy2(md_file, target_file)
                            else:
                                return {
                                    "error": "Could not find pack structure in archive",
                                }
                else:
                    return {"error": "Unsupported archive format"}
                
                return {
                    "success": True,
                    "message": f"Installed {pack_name} v{version} to cache",
                    "path": str(target_dir),
                }
            
            finally:
                # Clean up temp file
                if tmp_path.exists():
                    tmp_path.unlink()
        
        except Exception as e:
            return {
                "error": f"Failed to install pack: {str(e)}",
            }
    
    def use(self, pack_name: str, version: str, source: str = "cached") -> Dict:
        """Pin a prompt pack version in manifest.
        
        Args:
            pack_name: Pack name.
            version: Pack version.
            source: Source type ("cached" or "bundled").
            
        Returns:
            Dict with success status.
        """
        manifest = self._read_manifest()
        manifest["promptPack"] = {
            "name": pack_name,
            "version": version,
            "source": source,
        }
        
        try:
            self._write_manifest(manifest)
            return {
                "success": True,
                "message": f"Pinned {pack_name} v{version} (source: {source})",
            }
        except Exception as e:
            return {
                "error": f"Failed to update manifest: {str(e)}",
            }
    
    def verify(self, pack_name: str, version: str) -> Dict:
        """Verify prompt pack integrity.
        
        Args:
            pack_name: Pack name.
            version: Pack version.
            
        Returns:
            Dict with verification results.
        """
        pack_dir = self.cache_dir / pack_name / version
        
        if not pack_dir.exists():
            return {
                "error": f"Pack {pack_name} v{version} not found in cache",
            }
        
        # Check for required templates
        required_templates = {
            "new-project.md",
            "existing-project.md",
            "add-feature.md",
            "update-feature.md",
            "fix-bug.md",
            "create-agent.md",
            "learn-update.md",
        }
        
        found_templates = set()
        missing_templates = set()
        template_hashes = {}
        
        for template in required_templates:
            template_path = pack_dir / template
            if template_path.exists():
                found_templates.add(template)
                # Compute hash
                with open(template_path, "rb") as f:
                    content = f.read()
                    template_hashes[template] = hashlib.sha256(
                        content
                    ).hexdigest()
            else:
                missing_templates.add(template)
        
        return {
            "packName": pack_name,
            "version": version,
            "foundTemplates": list(found_templates),
            "missingTemplates": list(missing_templates),
            "templateHashes": template_hashes,
            "valid": len(missing_templates) == 0,
        }
