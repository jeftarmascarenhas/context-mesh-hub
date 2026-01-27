/** Start the local MCP server. */

import { spawnProcess } from "../utils/process.js";
import { ensureRepoRoot } from "../utils/repo.js";
import { readPid, isProcessRunning } from "../utils/process.js";

export async function startCommand(options: { port?: string }) {
  try {
    const repoRoot = ensureRepoRoot();
    
    // Check if server is already running
    const existingPid = readPid();
    if (existingPid && isProcessRunning(existingPid)) {
      console.log(`MCP server is already running (PID: ${existingPid})`);
      return;
    }
    
    console.log(`Starting MCP server for repository: ${repoRoot}`);
    
    // Find Python executable
    const pythonCmd = process.platform === "win32" ? "python" : "python3";
    
    // Spawn MCP server
    // In production, this would find the installed hub-core package
    const pid = spawnProcess(pythonCmd, [
      "-m", "hub_core.server",
      repoRoot,
    ], {
      cwd: repoRoot,
      env: {
        ...process.env,
        MCP_PORT: options.port || "8000",
      },
    });
    
    console.log(`✓ MCP server started (PID: ${pid})`);
    console.log(`  Port: ${options.port || "8000"}`);
    console.log(`  Repository: ${repoRoot}`);
  } catch (error) {
    console.error(`Error starting MCP server: ${error}`);
    process.exit(1);
  }
}
