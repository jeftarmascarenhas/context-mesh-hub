/** Check MCP server status. */

import { readPid, isProcessRunning } from "../utils/process.js";
import { ensureRepoRoot } from "../utils/repo.js";

export async function statusCommand() {
  try {
    const repoRoot = ensureRepoRoot();
    const pid = readPid();
    
    if (!pid) {
      console.log("Status: Not running (no PID file)");
      return;
    }
    
    if (isProcessRunning(pid)) {
      console.log(`Status: Running`);
      console.log(`  PID: ${pid}`);
      console.log(`  Repository: ${repoRoot}`);
      console.log(`\nTo stop: cm stop`);
    } else {
      console.log(`Status: Not running (PID ${pid} not found)`);
      console.log(`\nTo start: cm start`);
    }
  } catch (error) {
    console.error(`Error checking status: ${error}`);
    process.exit(1);
  }
}
