/** Utility functions for process management. */

import { spawn } from "cross-spawn";
import { existsSync, readFileSync, writeFileSync, unlinkSync } from "fs";
import { join } from "path";
import { platform } from "os";

const PID_FILE = join(process.cwd(), ".hub", "mcp-server.pid");

export function getPidFile(): string {
  return PID_FILE;
}

export function savePid(pid: number): void {
  const fs = require("fs");
  const path = require("path");
  const dir = path.dirname(PID_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(PID_FILE, pid.toString());
}

export function readPid(): number | null {
  if (!existsSync(PID_FILE)) {
    return null;
  }
  try {
    const pidStr = readFileSync(PID_FILE, "utf-8").trim();
    return parseInt(pidStr, 10);
  } catch {
    return null;
  }
}

export function removePidFile(): void {
  if (existsSync(PID_FILE)) {
    unlinkSync(PID_FILE);
  }
}

export function isProcessRunning(pid: number): boolean {
  try {
    // On Unix, signal 0 checks if process exists
    if (platform() !== "win32") {
      process.kill(pid, 0);
      return true;
    } else {
      // Windows: try to get process info
      const { execSync } = require("child_process");
      execSync(`tasklist /FI "PID eq ${pid}"`, { stdio: "ignore" });
      return true;
    }
  } catch {
    return false;
  }
}

export function spawnProcess(
  command: string,
  args: string[],
  options: { cwd?: string; env?: Record<string, string> } = {}
): number {
  const child = spawn(command, args, {
    ...options,
    stdio: "inherit",
    detached: true,
  });
  
  if (child.pid) {
    savePid(child.pid);
    child.unref(); // Allow parent to exit
    return child.pid;
  }
  
  throw new Error("Failed to spawn process");
}
