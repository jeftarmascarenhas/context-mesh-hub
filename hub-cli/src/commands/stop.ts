/** Stop the local MCP server. */

import { readPid, removePidFile, isProcessRunning } from "../utils/process.js";
import { platform } from "os";

export async function stopCommand() {
  const pid = readPid();
  
  if (!pid) {
    console.log("No MCP server process found (no PID file)");
    return;
  }
  
  if (!isProcessRunning(pid)) {
    console.log(`MCP server process not running (PID: ${pid} not found)`);
    removePidFile();
    return;
  }
  
  try {
    // Terminate process
    if (platform() !== "win32") {
      process.kill(pid, "SIGTERM");
    } else {
      const { execSync } = require("child_process");
      execSync(`taskkill /PID ${pid} /F`, { stdio: "ignore" });
    }
    
    console.log(`✓ MCP server stopped (PID: ${pid})`);
    removePidFile();
  } catch (error) {
    console.error(`Error stopping MCP server: ${error}`);
    process.exit(1);
  }
}
