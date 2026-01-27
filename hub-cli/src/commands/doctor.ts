/** Run diagnostics and check environment. */

import { existsSync } from "fs";
import { join } from "path";
import { execSync } from "child_process";
import { findRepoRoot } from "../utils/repo.js";

interface Diagnostic {
  name: string;
  status: "pass" | "fail" | "warning";
  message: string;
  remediation?: string;
}

export async function doctorCommand() {
  const diagnostics: Diagnostic[] = [];
  
  // Check Node.js version
  try {
    const nodeVersion = process.version;
    const major = parseInt(nodeVersion.slice(1).split(".")[0], 10);
    if (major >= 20) {
      diagnostics.push({
        name: "Node.js version",
        status: "pass",
        message: `Node.js ${nodeVersion} (Active LTS required: >=20.0.0)`,
      });
    } else {
      diagnostics.push({
        name: "Node.js version",
        status: "fail",
        message: `Node.js ${nodeVersion} (Active LTS required: >=20.0.0)`,
        remediation: "Upgrade Node.js to Active LTS version (20.x or later)",
      });
    }
  } catch {
    diagnostics.push({
      name: "Node.js version",
      status: "fail",
      message: "Node.js not found",
      remediation: "Install Node.js Active LTS (20.x or later)",
    });
  }
  
  // Check Python version
  try {
    const pythonCmd = process.platform === "win32" ? "python" : "python3";
    const pythonVersion = execSync(`${pythonCmd} --version`, { encoding: "utf-8" }).trim();
    const match = pythonVersion.match(/Python (\d+)\.(\d+)/);
    if (match) {
      const major = parseInt(match[1], 10);
      const minor = parseInt(match[2], 10);
      if (major > 3 || (major === 3 && minor >= 12)) {
        diagnostics.push({
          name: "Python version",
          status: "pass",
          message: `${pythonVersion} (required: >=3.12)`,
        });
      } else {
        diagnostics.push({
          name: "Python version",
          status: "fail",
          message: `${pythonVersion} (required: >=3.12)`,
          remediation: "Upgrade Python to 3.12 or later",
        });
      }
    }
  } catch {
    diagnostics.push({
      name: "Python version",
      status: "fail",
      message: "Python 3.12+ not found",
      remediation: "Install Python 3.12 or later",
    });
  }
  
  // Check repository structure
  const repoRoot = findRepoRoot();
  if (repoRoot) {
    const contextDir = join(repoRoot, "context");
    if (existsSync(contextDir)) {
      diagnostics.push({
        name: "Repository structure",
        status: "pass",
        message: `Context directory found: ${contextDir}`,
      });
      
      // Check required subdirectories
      const requiredDirs = ["intent", "decisions", "evolution"];
      const missingDirs = requiredDirs.filter(
        dir => !existsSync(join(contextDir, dir))
      );
      
      if (missingDirs.length === 0) {
        diagnostics.push({
          name: "Context structure",
          status: "pass",
          message: "All required directories present",
        });
      } else {
        diagnostics.push({
          name: "Context structure",
          status: "warning",
          message: `Missing directories: ${missingDirs.join(", ")}`,
          remediation: "Run 'cm init' to create missing directories",
        });
      }
    } else {
      diagnostics.push({
        name: "Repository structure",
        status: "warning",
        message: "Context directory not found",
        remediation: "Run 'cm init' to initialize Context Mesh Hub",
      });
    }
  } else {
    diagnostics.push({
      name: "Repository structure",
      status: "warning",
      message: "Not in a repository",
      remediation: "Run 'cm init' to initialize Context Mesh Hub",
    });
  }
  
  // Print diagnostics
  console.log("Context Mesh Hub Diagnostics\n");
  console.log("=" .repeat(50));
  
  for (const diag of diagnostics) {
    const icon = diag.status === "pass" ? "✓" : diag.status === "fail" ? "✗" : "⚠";
    const status = diag.status.toUpperCase().padEnd(7);
    console.log(`${icon} [${status}] ${diag.name}`);
    console.log(`   ${diag.message}`);
    if (diag.remediation) {
      console.log(`   → ${diag.remediation}`);
    }
    console.log();
  }
  
  const fails = diagnostics.filter(d => d.status === "fail").length;
  const warnings = diagnostics.filter(d => d.status === "warning").length;
  
  if (fails > 0) {
    console.log(`\n✗ ${fails} issue(s) found that must be resolved`);
    process.exit(1);
  } else if (warnings > 0) {
    console.log(`\n⚠ ${warnings} warning(s) - review recommended`);
  } else {
    console.log(`\n✓ All checks passed!`);
  }
}
