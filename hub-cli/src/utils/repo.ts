/** Utility functions for repository operations. */

import { existsSync } from "fs";
import { join, dirname, resolve } from "path";
import { statSync } from "fs";

export function findRepoRoot(startPath: string = process.cwd()): string | null {
  /** Find repository root by looking for .git or context/ directory. */
  let current = resolve(startPath);
  
  while (current !== dirname(current)) {
    if (existsSync(join(current, ".git")) || 
        existsSync(join(current, "context"))) {
      return current;
    }
    current = dirname(current);
  }
  
  return null;
}

export function ensureRepoRoot(): string {
  /** Ensure we're in a repository, throw if not. */
  const root = findRepoRoot();
  if (!root) {
    throw new Error(
      "Not in a repository. Run 'cm init' to initialize Context Mesh Hub."
    );
  }
  return root;
}
