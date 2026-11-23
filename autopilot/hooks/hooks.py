#!/usr/bin/env python3
"""
hooks.py — the mechanical guard for the IoT-23 project.

Antigravity calls these from `.agents/hooks.json` on lifecycle events. They receive the
event payload as JSON on stdin and must print a JSON object on stdout.

Why this exists: in headless mode (`agy -p`) a tool that would normally prompt is
*soft-denied* — the run continues, exits 0, and prints a notice to stderr. So "exit 0"
does not mean the work happened. This hook does two things about that:

  1. auto-approves the read-only and pipeline commands the agents legitimately need,
     so they are not soft-denied;
  2. hard-denies the handful of commands that would break a core project rule,
     regardless of which agent is running or what the prompt says.

The rules therefore survive a model that ignores its instructions.

Subcommands: pretool | posttool | session | stop
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("IDP_REPO", "/home/harish/IDP-LOCAL"))
LOG_DIR = ROOT / "autopilot" / "logs"

# ---------------------------------------------------------------- deny rules
# Each entry: (compiled pattern, reason shown to the agent)
DENY: list[tuple[re.Pattern, str]] = [
    (re.compile(r"git\s+push\b[^\n]*--force|git\s+push\b[^\n]*\s-f\b"),
     "Force-push is forbidden: it rewrites history on a branch the manager reviews."),
    (re.compile(r"git\s+push\b[^\n]*\b(origin\s+)?(main|master)\b"),
     "Direct push to main is forbidden. Raise a PR; only the manager merges."),
    (re.compile(r"git\s+reset\s+--hard"),
     "git reset --hard is forbidden: it destroys uncommitted review evidence."),
    (re.compile(r"git\s+commit\b[^\n]*--no-verify"),
     "Skipping hooks is forbidden: the hooks are the project's guard rails."),
    (re.compile(r"rm\s+-[a-z]*r[a-z]*f?\s+(/|~|/\*|data/raw|\.\.)"),
     "Recursive delete of a protected path is forbidden."),
    (re.compile(r"(>|>>|tee|cp|mv|sed\s+-i|truncate)[^\n]*\bdata/raw"),
     "Raw data is read-only. Write to a working directory and log the copy's checksum."),
    (re.compile(r"kaggle\s+datasets\s+(delete|unshare)"),
     "Deleting a published dataset version is forbidden: publication is reversible, deletion is not."),
    (re.compile(r"git\s+tag\b[^\n]*\s(-f|--force)"),
     "Re-tagging a released version is forbidden: supersede it, do not overwrite it."),
    (re.compile(r"chmod\s+777"),
     "chmod 777 is forbidden: it defeats least privilege on the workspace."),
]

# ------------------------------------------------------- auto-approve rules
# Read-only and pipeline commands that headless mode would otherwise soft-deny.
AUTO: list[re.Pattern] = [
    re.compile(r"^\s*git\s+(status|diff|log|show|branch|rev-parse|remote|ls-files|tag\s+--list)\b"),
    re.compile(r"^\s*gh\s+pr\s+(view|checks|list|diff|status)\b"),
    re.compile(r"^\s*gh\s+issue\s+(view|list)\b"),
    re.compile(r"^\s*kaggle\s+kernels\s+(status|output|list)\b"),
    re.compile(r"^\s*kaggle\s+datasets\s+(list|files|metadata)\b"),
    re.compile(r"^\s*(pytest|python3?\s+-m\s+pytest|ruff|black|make\s+(test|test-full|gate|lint))\b"),
    re.compile(r"^\s*(ls|cat|head|tail|wc|du|df|find|grep|rg|jq|sha256sum|tree|stat)\b"),
    re.compile(r"^\s*python3?\s+autopilot/(model_router|autopilot)\.py\b"),
]

# Commands that change state but are legitimate and expected — allow, do not auto-approve
ALLOW_STATE_CHANGING = re.compile(
    r"^\s*(git\s+(add|commit|switch|checkout|merge|pull|fetch|stash|push)|"
    r"gh\s+pr\s+(create|comment|review)|"
    r"kaggle\s+kernels\s+push|kaggle\s+datasets\s+(create|version)|"
    r"pip|python3?\s+autopilot/hooks/hooks\.py)\b"
)


def emit(obj: dict) -> None:
    print(json.dumps(obj))
    sys.exit(0)


def read_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def tool_command(payload: dict) -> str:
    """Extract the shell command without depending on the exact args key name."""
    args = (payload.get("toolCall") or {}).get("args") or {}
    if isinstance(args, str):
        return args
    parts = [str(v) for v in args.values() if isinstance(v, (str, int, float))]
    return " \n".join(parts)


def audit(event: str, payload: dict, extra: dict) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": dt.datetime.now().replace(microsecond=0).isoformat(),
            "event": event,
            "model": payload.get("modelName"),
            "conversation": payload.get("conversationId"),
            **extra,
        }
        with (LOG_DIR / "hooks.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def pretool(payload: dict) -> None:
    cmd = tool_command(payload)
    name = (payload.get("toolCall") or {}).get("name", "")

    for pattern, reason in DENY:
        if pattern.search(cmd):
            audit("deny", payload, {"tool": name, "command": cmd[:400], "reason": reason})
            emit({"decision": "deny", "reason": reason})

    for pattern in AUTO:
        if pattern.search(cmd):
            audit("auto_approve", payload, {"tool": name, "command": cmd[:400]})
            emit({"decision": "auto_approve", "reason": "read-only or pipeline command"})

    if ALLOW_STATE_CHANGING.search(cmd):
        audit("allow", payload, {"tool": name, "command": cmd[:400]})
        emit({"decision": "allow"})

    # Anything else: hand it to the default policy, which asks in interactive mode
    # and soft-denies in headless mode. That is the intended behaviour for unknown
    # state-changing commands.
    audit("allow_default", payload, {"tool": name, "command": cmd[:400]})
    emit({"decision": "allow"})


def posttool(payload: dict) -> None:
    tool = (payload.get("toolCall") or {}).get("name", "")
    if tool == "replace_file_content":
        args = (payload.get("toolCall") or {}).get("args") or {}
        audit("edit", payload, {"tool": tool, "target": str(args.get("TargetFile") or args.get("target_file") or "")[:300]})
    elif tool == "run_command":
        audit("command", payload, {"command": tool_command(payload)[:400], "error": payload.get("error", "")[:200]})
    emit({})


def session(payload: dict) -> None:
    """Log the branch. A session started on main is a warning, not a block."""
    branch = ""
    try:
        import subprocess

        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except Exception:
        pass
    audit("session_start", payload, {"branch": branch})
    emit({})


def stop(payload: dict) -> None:
    audit("stop", payload, {"reason": payload.get("terminationReason"), "fullyIdle": payload.get("fullyIdle")})
    emit({})


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    payload = read_payload()
    if action == "pretool":
        pretool(payload)
    elif action == "posttool":
        posttool(payload)
    elif action == "session":
        session(payload)
    elif action == "stop":
        stop(payload)
    else:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
