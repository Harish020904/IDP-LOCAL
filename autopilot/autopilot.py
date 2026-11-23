#!/usr/bin/env python3
"""
autopilot.py — unattended driver for the IoT-23 pipeline.

Two modes
---------
1. Bounded (default): build the thirteen stages in order, then stop.
2. Endless (--until-exhausted): keep working until the model budget runs out.
   After stage 12 it starts another audit pass — the tester re-verifies every stage
   from scratch, and any finding drops that stage back into the full build -> review ->
   verify -> merge cycle. It never invents new work and never weakens a gate; it keeps
   proving the dataset is what the reports say it is, until the quota stops it.

Exit codes
----------
    0  finished (bounded mode complete, or a cap was reached)
    3  quota exhausted — every model in the chain, including the floor, is cooling
    4  blocked — S1 veto, attempt cap, merge gate failure, or repeated turn failures
    5  no transition — the state machine refused to move; nothing was consumed

Phases per stage
----------------
    todo -> build -> review -> verify -> merge -> done
                        |         |
                        +---------+--> build   (rework, capped by --max-attempts)
    verify with s1 > 0                     -> blocked (S1 veto, no auto-rework)

In endless mode a stage that is already built starts at `verify` instead of `build`.

Branch model (per the project page)
-----------------------------------
Stage PRs target `EDL-Pipeline`. The milestone PR from `EDL-Pipeline` to `main` stays a
human decision — this driver never opens or merges it.

Usage
-----
    python3 autopilot/autopilot.py --dry-run --stage 0 --once
    python3 autopilot/autopilot.py --stage 0
    python3 autopilot/autopilot.py --max-stages 3
    python3 autopilot/autopilot.py --until-exhausted            # until quota runs out
    python3 autopilot/autopilot.py --until-exhausted --max-hours 6
    python3 autopilot/autopilot.py --status
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from model_router import Router, QuotaExhausted  # noqa: E402

ROOT = pathlib.Path(os.environ.get("IDP_REPO", "/home/harish/IDP-LOCAL"))
HERE = pathlib.Path(__file__).resolve().parent
STATE_PATH = HERE / "state.json"
LOG_DIR = HERE / "logs"
AGY = os.environ.get("AGY_BIN", "agy")

BASE_BRANCH = "EDL-Pipeline"

STAGES = {
    0: "definition and preparation",
    1: "dataset acquisition and integrity verification",
    2: "raw dataset inventory",
    3: "understand the raw Zeek schema",
    4: "raw data profiling and visualisation",
    5: "data quality assessment",
    6: "raw data cleaning",
    7: "feature classification and governance",
    8: "data partitioning",
    9: "data preprocessing and transformation",
    10: "storage format and dataset organisation",
    11: "data integrity and reproducibility testing",
    12: "understand and document the class imbalance",
}

PHASES = {
    "build": ("data-engineer", "build", "prompts/build.md"),
    "review": ("manager", "review", "prompts/review.md"),
    "verify": ("tester", "verify", "prompts/verify.md"),
}

SCHEMAS = {
    "build": {
        "type": "object",
        "required": ["status", "summary"],
        "properties": {
            "status": {"enum": ["built", "blocked", "failed"]},
            "summary": {"type": "string"},
            "files_changed": {"type": "array", "items": {"type": "string"}},
            "kernel": {"type": "string"},
            "numbers": {"type": "object"},
            "tests": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer"},
                    "passing": {"type": "integer"},
                    "criteria_covered": {"type": "integer"},
                    "criteria_total": {"type": "integer"},
                },
            },
            "blockers": {"type": "array", "items": {"type": "string"}},
        },
    },
    "review": {
        "type": "object",
        "required": ["decision", "blocking"],
        "properties": {
            "decision": {"enum": ["approve", "request_changes", "close"]},
            "blocking": {"type": "array", "items": {"type": "string"}},
            "checked": {
                "type": "object",
                "properties": {
                    "scope": {"type": "boolean"},
                    "evidence": {"type": "boolean"},
                    "tests": {"type": "boolean"},
                    "docs": {"type": "boolean"},
                    "invariants": {"type": "boolean"},
                    "reversibility": {"type": "boolean"},
                },
            },
        },
    },
    "verify": {
        "type": "object",
        "required": ["verdict", "s1", "s2", "s3", "s4", "recommend"],
        "properties": {
            "verdict": {"enum": ["PASS", "PASS WITH CONDITIONS", "FAIL"]},
            "s1": {"type": "integer"},
            "s2": {"type": "integer"},
            "s3": {"type": "integer"},
            "s4": {"type": "integer"},
            "evidence": {"type": "string"},
            "recommend": {"enum": ["merge", "rework", "retest"]},
            "review_file": {"type": "string"},
        },
    },
}


# ------------------------------------------------------------------ utilities
def now() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


def log(event: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"autopilot-{now():%Y%m%d}.jsonl"
    with path.open("a") as fh:
        fh.write(json.dumps({"ts": now().isoformat(), **event}) + "\n")


def sh(cmd: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True)


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            data = json.loads(STATE_PATH.read_text())
            data.setdefault("pass", 1)
            data.setdefault("audit", False)
            return data
        except json.JSONDecodeError:
            pass
    return {"stage": 0, "phase": "build", "attempt": 1, "pass": 1, "audit": False, "history": [], "blocked": None}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def stage_is_built(stage: int) -> bool:
    d = ROOT / "docs" / "02-stages"
    return d.exists() and bool(list(d.glob(f"stage-{stage:02d}*")))


def review_file(stage: int) -> pathlib.Path:
    d = ROOT / "docs" / "03-reviews"
    matches = sorted(d.glob(f"*stage-{stage:02d}*")) if d.exists() else []
    return matches[-1] if matches else d / f"stage-{stage:02d}-review.md"


def out_dir(stage: int) -> pathlib.Path:
    return ROOT / "out" / f"stage-{stage:02d}"


def entry_phase(stage: int, endless: bool) -> str:
    """Where to start a stage. Already-built stages are re-verified, not rebuilt."""
    if endless and stage_is_built(stage):
        return "verify"
    return "build"


# ------------------------------------------------------------------ the agy call
def run_turn(agent: str, task_class: str, prompt: str, router: Router, timeout: str, dry_run: bool) -> dict:
    try:
        model = router.pick(task_class)
    except QuotaExhausted as exc:
        return {"ok": False, "status": "EXHAUSTED", "error": str(exc), "data": {}, "model": None}

    schema = json.dumps(SCHEMAS[task_class])

    # Flag order matters: --model must precede -p. In headless mode -p swallows the
    # argument that follows it, so a trailing --model is silently ignored and the run
    # falls back to the default model with exit 0. Every flag goes before the prompt.
    cmd = [
        AGY,
        "--model", model,
        "--agent", agent,
        "--output-format", "json",
        "--json-schema", schema,
        "--print-timeout", timeout,
    ]
    effort = router.effort(task_class)
    if effort:
        cmd += ["--effort", effort]

    mode = (router.policy.get("agy_mode") or "").strip()
    if mode:
        cmd += ["--mode", mode]

    cmd += ["-p", prompt]

    if dry_run:
        shown = " ".join(cmd[: cmd.index("-p")])
        print(f"\n[dry-run] {shown} -p <{len(prompt)} chars>")
        return {"ok": True, "status": "DRY", "data": {}, "model": model, "error": "", "soft_denied": False}

    log({"event": "agy_call", "agent": agent, "task": task_class, "model": model})
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=7200)
    except subprocess.TimeoutExpired:
        router.record(model, False, "timeout")
        return {"ok": False, "status": "TIMEOUT", "error": "print-timeout exceeded", "data": {}, "model": model}

    stderr = proc.stderr or ""
    try:
        envelope = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        envelope = {}

    status = envelope.get("status") or ("SUCCESS" if proc.returncode == 0 else "ERROR")
    error = envelope.get("error") or (stderr.strip()[-2000:] if proc.returncode != 0 else "")

    # exit 0 does not mean the work happened: tools needing approval are soft-denied
    soft_denied = bool(
        re.search(r"requires approval|soft[- ]denied|not permitted|permission", stderr, re.I)
    ) and proc.returncode == 0

    data: dict = {}
    payload = envelope.get("response")
    if isinstance(payload, dict):
        data = payload
    elif isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {}

    ok = status == "SUCCESS" and proc.returncode == 0 and bool(data) and not soft_denied
    limit_error = (not ok) and router.is_limit_error(error or stderr)
    router.record(model, ok, error or stderr)
    log(
        {
            "event": "agy_result",
            "agent": agent,
            "model": model,
            "status": status,
            "exit": proc.returncode,
            "soft_denied": soft_denied,
            "limit_error": limit_error,
            "ok": ok,
            "data": data,
        }
    )
    return {
        "ok": ok,
        "status": status,
        "data": data,
        "model": model,
        "error": error,
        "soft_denied": soft_denied,
        "limit_error": limit_error,
    }


def build_prompt(task_class: str, stage: int, state: dict, extra: str = "") -> str:
    tpl = (HERE / PHASES[task_class][2]).read_text()
    return (
        tpl.replace("{stage}", str(stage))
        .replace("{stage_name}", STAGES[stage])
        .replace("{attempt}", str(state.get("attempt", 1)))
        .replace("{stage_pad}", f"{stage:02d}")
        .replace("{defects}", extra or "none")
        .replace("{pass}", str(state.get("pass", 1)))
        .replace("{base_branch}", BASE_BRANCH)
    )


# ------------------------------------------------------------------ gates
def gate_build(stage: int) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not stage_is_built(stage):
        problems.append(f"no stage note for stage {stage:02d}")
    od = out_dir(stage)
    if not od.exists():
        problems.append(f"no output directory {od.relative_to(ROOT)}")
    elif not (od / "run.log").exists():
        problems.append("no run.log pulled from the Kaggle run")
    return (not problems, problems)


def gate_merge(stage: int, review: dict, verify: dict) -> tuple[bool, list[str]]:
    """The two-key gate. Checked here, in code, against files on disk."""
    problems: list[str] = []

    if review.get("decision") != "approve":
        problems.append(f"manager decision is {review.get('decision')!r}, not 'approve'")

    verdict = verify.get("verdict")
    if verdict not in ("PASS", "PASS WITH CONDITIONS"):
        problems.append(f"tester verdict is {verdict!r}")

    if int(verify.get("s1") or 0) > 0:
        problems.append(f"{verify.get('s1')} S1 defect(s) open — veto")
    if int(verify.get("s2") or 0) > 0:
        problems.append(f"{verify.get('s2')} S2 defect(s) open")

    rf = review_file(stage)
    if not rf.exists():
        problems.append(f"review file missing: {rf.relative_to(ROOT)}")
    elif not re.search(r"VERDICT:\s*(PASS|PASS WITH CONDITIONS)", rf.read_text(), re.I):
        problems.append("review file does not record a PASS verdict")

    st = sh(["git", "status", "--porcelain"])
    if st.returncode == 0 and st.stdout.strip():
        problems.append("worktree is dirty — commit or stash before merge")

    pr = pr_number()
    if pr:
        checks = sh(["gh", "pr", "checks", str(pr)])
        if checks.returncode != 0 and "no checks" not in (checks.stdout + checks.stderr).lower():
            problems.append(f"PR #{pr} checks are not green")

    return (not problems, problems)


def pr_number() -> int | None:
    out = sh(["gh", "pr", "view", "--json", "number", "-q", ".number"])
    if out.returncode != 0:
        return None
    try:
        return int(out.stdout.strip())
    except ValueError:
        return None


def do_merge(stage: int, dry_run: bool) -> tuple[bool, str]:
    pr = pr_number()
    if pr is None:
        return False, "no open PR for the current branch"
    if dry_run:
        print(f"[dry-run] gh pr merge {pr} --squash --delete-branch")
        return True, f"dry-run merge of PR #{pr}"
    out = sh(["gh", "pr", "merge", str(pr), "--squash", "--delete-branch"])
    if out.returncode != 0:
        return False, (out.stderr or out.stdout).strip()[:500]
    return True, f"merged PR #{pr}"


# ------------------------------------------------------------------ transitions
def advance(state: dict, phase: str, result: dict, audit: bool) -> dict:
    stage = state["stage"]
    data = result.get("data") or {}

    if not result["ok"]:
        state["history"].append(
            {"ts": now().isoformat(), "stage": stage, "phase": phase, "result": "error", "error": (result.get("error") or "")[:300]}
        )
        state["blocked"] = {
            "stage": stage,
            "reason": "all models exhausted" if result["status"] == "EXHAUSTED" else f"{phase} turn failed",
            "detail": (result.get("error") or "")[:500],
            "soft_denied": result.get("soft_denied", False),
            "exhausted": result["status"] == "EXHAUSTED",
        }
        return state

    if phase == "build":
        status = data.get("status", "failed")
        if status == "built":
            state["phase"] = "review"
        else:
            state["blocked"] = {"stage": stage, "reason": f"build reported {status}", "detail": data.get("blockers", [])}
        return state

    if phase == "review":
        decision = data.get("decision")
        if decision == "approve":
            state["phase"] = "verify"
        elif decision == "request_changes":
            state["attempt"] += 1
            state["phase"] = "build"
            state["last_defects"] = data.get("blocking", [])
        else:
            state["blocked"] = {"stage": stage, "reason": "manager closed the PR", "detail": data.get("blocking", [])}
        return state

    if phase == "verify":
        verdict = data.get("verdict")
        if int(data.get("s1") or 0) > 0:
            state["blocked"] = {"stage": stage, "reason": "S1 defect — veto", "detail": data}
            state["phase"] = "blocked"
            return state
        if verdict in ("PASS", "PASS WITH CONDITIONS"):
            if audit:
                # nothing to merge: the stage already exists and has just re-passed
                state["stage"] = stage + 1
                state["phase"] = "verify"
            else:
                state["phase"] = "merge"
        else:
            state["attempt"] += 1
            state["phase"] = "build"
            state["last_defects"] = [f"S2 x{data.get('s2')}", f"S3 x{data.get('s3')}", data.get("evidence", "")]
        return state

    return state


def summary(state: dict, router: Router, reason: str) -> None:
    print("\n" + "=" * 68)
    print(f"stopped: {reason}")
    print(
        f"stage {state['stage']:02d} · phase {state['phase']} · pass {state.get('pass', 1)} "
        f"· attempt {state.get('attempt', 1)}"
    )
    merged = [h for h in state.get("history", []) if h.get("phase") == "merge"]
    print(f"merged this run: {len(merged)}")
    try:
        ledger = router.ledger()
        cooling = {k: v.get("cooldown_until") for k, v in ledger.items() if v.get("cooldown_until")}
        if cooling:
            print("cooling down:")
            for slug, until in cooling.items():
                print(f"  {slug:34} until {until}")
        earliest = router.earliest_expiry()
        if earliest:
            print(f"earliest recovery: {earliest.isoformat()}")
    except Exception:
        pass
    print("=" * 68)


# ------------------------------------------------------------------ the loop
def run(args) -> int:
    router = Router(
        policy_path=HERE / "policy.yaml",
        ledger_path=HERE / "model_ledger.json",
        agy=AGY,
    )
    state = load_state()

    if args.reset_stage is not None:
        state = {
            "stage": args.reset_stage, "phase": "build", "attempt": 1, "pass": 1,
            "audit": False, "history": state.get("history", []), "blocked": None,
        }
        save_state(state)
        print(f"stage {args.reset_stage} rewound to build")
        return 0

    if args.status:
        print(json.dumps(state, indent=2))
        return 0

    if args.stage is not None:
        state["stage"] = args.stage
        state["phase"] = entry_phase(args.stage, args.until_exhausted)
        state["attempt"] = 1
        state["blocked"] = None

    started = now()
    merged_count = 0
    consecutive_failures = 0
    limit_retries = 0

    while True:
        stage = state["stage"]
        phase = state["phase"]

        # ---- stop conditions -------------------------------------------------
        if args.max_hours and (now() - started).total_seconds() > args.max_hours * 3600:
            summary(state, router, f"max-hours reached ({args.max_hours}h)")
            save_state(state)
            return 0

        if state.get("blocked"):
            blocked = state["blocked"]
            if blocked.get("exhausted"):
                summary(state, router, "quota exhausted — every model is cooling down")
                state["blocked"] = None
                save_state(state)
                return 3
            print(f"\nBLOCKED at stage {stage:02d} / {phase}: {blocked.get('reason')}")
            print(json.dumps(blocked.get("detail", ""), indent=2)[:1200])
            save_state(state)
            return 4

        if stage > 12:
            if not args.until_exhausted:
                print("\nall thirteen stages complete")
                save_state(state)
                return 0
            state["pass"] = state.get("pass", 1) + 1
            if args.max_passes and state["pass"] > args.max_passes:
                summary(state, router, f"max-passes reached ({args.max_passes})")
                save_state(state)
                return 0
            state.update({"stage": 0, "phase": entry_phase(0, True), "attempt": 1, "audit": True})
            print(f"\n--- pass {state['pass']}: audit sweep, stages 0-12 re-verified ---")
            save_state(state)
            continue

        # ---- merge is deterministic, never model-driven ----------------------
        if phase == "merge":
            ok, detail = gate_merge(stage, state.get("review", {}), state.get("verify", {}))
            if not ok:
                print(f"\nMERGE REFUSED at stage {stage:02d}:")
                for p in detail:
                    print(f"  - {p}")
                state["blocked"] = {"stage": stage, "reason": "merge gates failed", "detail": detail}
                save_state(state)
                return 4
            merged, msg = do_merge(stage, args.dry_run)
            print(f"  merge: {msg}")
            log({"event": "merge", "stage": stage, "ok": merged, "msg": msg})
            if not merged:
                state["blocked"] = {"stage": stage, "reason": "merge failed", "detail": msg}
                save_state(state)
                return 4
            state["history"].append({"ts": now().isoformat(), "stage": stage, "phase": "merge", "result": "done"})
            state.update(
                {
                    "stage": stage + 1,
                    "phase": entry_phase(stage + 1, args.until_exhausted),
                    "attempt": 1,
                    "audit": args.until_exhausted,
                }
            )
            state.pop("review", None)
            state.pop("verify", None)
            state.pop("last_defects", None)
            save_state(state)
            merged_count += 1
            consecutive_failures = 0
            limit_retries = 0
            if args.max_stages and merged_count >= args.max_stages:
                summary(state, router, f"max-stages reached ({args.max_stages})")
                return 0
            continue

        # ---- attempt cap -----------------------------------------------------
        if state.get("attempt", 1) > args.max_attempts:
            state["blocked"] = {
                "stage": stage,
                "reason": f"attempt cap reached ({args.max_attempts})",
                "detail": state.get("last_defects", []),
            }
            save_state(state)
            print(f"\nBLOCKED: stage {stage:02d} exceeded {args.max_attempts} attempts — human needed")
            return 4

        # ---- one turn --------------------------------------------------------
        agent, task_class, _ = PHASES[phase]
        extra = ""
        if phase == "build" and state.get("last_defects"):
            extra = "\n".join(f"- {d}" for d in state["last_defects"])
        prompt = build_prompt(task_class, stage, state, extra)

        audit_now = bool(state.get("audit")) and phase == "verify"
        mode_tag = " · audit" if audit_now else ""
        print(
            f"\n[{now():%H:%M:%S}] pass {state.get('pass', 1)} · stage {stage:02d} ({STAGES[stage]}) "
            f"· {phase} · attempt {state.get('attempt', 1)}{mode_tag}"
        )
        result = run_turn(agent, task_class, prompt, router, args.print_timeout, args.dry_run)
        print(f"  agent={agent} model={result.get('model')} status={result.get('status')} ok={result['ok']}")
        if result.get("soft_denied"):
            print("  WARNING: a tool call was soft-denied — exit 0 does not mean the work happened")

        # A model out of budget is not a project failure: drop down the chain and retry
        # the same phase. Only when every model, including the floor, is cooling do we
        # stop — that is the natural end of an endless run.
        if result.get("status") == "EXHAUSTED":
            summary(state, router, "quota exhausted — every model is cooling down")
            save_state(state)
            return 3

        if not result["ok"] and result.get("limit_error"):
            limit_retries += 1
            print(f"  model {result.get('model')} out of budget — falling back")
            log({"event": "model_exhausted", "model": result.get("model"), "stage": stage, "phase": phase})
            if limit_retries > 15:
                summary(state, router, "too many model fallbacks")
                save_state(state)
                return 3
            continue

        if phase == "review":
            state["review"] = result.get("data") or {}
        if phase == "verify":
            state["verify"] = result.get("data") or {}

        state = advance(state, phase, result, audit_now)

        # a model claiming "built" is not evidence — check the filesystem
        if phase == "build" and state.get("phase") == "review" and not state.get("blocked"):
            ok, problems = gate_build(stage)
            if not ok:
                print("  build gate failed — sending back to build")
                for p in problems:
                    print(f"    - {p}")
                state["attempt"] += 1
                state["phase"] = "build"
                state["last_defects"] = problems

        # leaving audit mode for a real fix cycle
        if state.get("audit") and state.get("phase") == "build":
            state["audit"] = False

        state["history"].append(
            {
                "ts": now().isoformat(),
                "pass": state.get("pass", 1),
                "stage": stage,
                "phase": phase,
                "model": result.get("model"),
                "status": result.get("status"),
            }
        )
        save_state(state)

        if result["ok"]:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if consecutive_failures >= args.max_failures:
                summary(state, router, f"{consecutive_failures} consecutive failed turns")
                return 4

        if state["phase"] == phase and not state.get("blocked"):
            print("  no transition — stopping to avoid a loop")
            return 5

        if args.once:
            return 0

        if args.sleep:
            time.sleep(args.sleep)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="IoT-23 autopilot")
    ap.add_argument("--stage", type=int, help="force a starting stage (0-12)")
    ap.add_argument("--max-stages", type=int, default=0, help="stop after N merged stages")
    ap.add_argument("--max-attempts", type=int, default=3, help="rework attempts per stage")
    ap.add_argument("--print-timeout", default="45m", help="per-turn limit, e.g. 45m")
    ap.add_argument("--once", action="store_true", help="run a single phase then exit")
    ap.add_argument("--dry-run", action="store_true", help="print commands, call nothing")
    ap.add_argument("--status", action="store_true", help="print state and exit")
    ap.add_argument("--reset-stage", type=int, help="rewind a stage to build")
    ap.add_argument("--until-exhausted", action="store_true", help="run endlessly until the model quota runs out")
    ap.add_argument("--max-passes", type=int, default=0, help="cap on full audit sweeps (0 = unlimited)")
    ap.add_argument("--max-hours", type=float, default=0, help="wall-clock guard in hours (0 = unlimited)")
    ap.add_argument("--max-failures", type=int, default=3, help="consecutive failed turns before stopping")
    ap.add_argument("--sleep", type=int, default=3, help="seconds between turns")
    args = ap.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
