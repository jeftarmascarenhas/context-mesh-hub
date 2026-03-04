"""CLI commands for Context Mesh Hub.

Slash commands following the Intent → Build → Learn workflow:
- /intent - Define WHAT and WHY (new-project, add-feature, fix-bug)
- /build  - Plan, Approve, Execute
- /learn  - Sync learnings, update context

Additional commands:
- /skills - Manage Context Mesh skills for AI agents
"""

from hub_cli.commands.intent import intent_app
from hub_cli.commands.build import build_app
from hub_cli.commands.learn import learn_app
from hub_cli.commands.skills import skills_app

__all__ = ["intent_app", "build_app", "learn_app", "skills_app"]
