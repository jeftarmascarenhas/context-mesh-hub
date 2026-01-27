#!/usr/bin/env node

import { Command } from "commander";
import { initCommand } from "./commands/init.js";
import { startCommand } from "./commands/start.js";
import { stopCommand } from "./commands/stop.js";
import { statusCommand } from "./commands/status.js";
import { uiCommand } from "./commands/ui.js";
import { doctorCommand } from "./commands/doctor.js";

const program = new Command();

program
  .name("cm")
  .description("Context Mesh Hub CLI - Bootstrap, runtime, and diagnostics")
  .version("0.1.0");

program
  .command("init")
  .description("Initialize Context Mesh Hub in the current repository")
  .option("--force", "Overwrite existing files")
  .action(initCommand);

program
  .command("start")
  .description("Start the local MCP server")
  .option("-p, --port <port>", "MCP server port", "8000")
  .action(startCommand);

program
  .command("stop")
  .description("Stop the local MCP server")
  .action(stopCommand);

program
  .command("status")
  .description("Check MCP server status")
  .action(statusCommand);

program
  .command("ui")
  .description("Launch the local UI")
  .option("--open", "Open browser automatically")
  .option("-p, --port <port>", "UI server port", "3000")
  .action(uiCommand);

program
  .command("doctor")
  .description("Run diagnostics and check environment")
  .action(doctorCommand);

program.parse();
