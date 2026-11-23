#!/usr/bin/env python3
"""
model_router.py — choose a model per task, track exhaustion, fall back to Flash 3.8.

Design notes
------------
* Model slugs are read from `agy models`, never hardcoded as the only source of truth.
  The policy lists *candidate* slugs; anything the account does not expose is skipped.
* `agy --model <slug>` HARD-FAILS on an unknown slug (exit 1) in headless mode, which is
  what we want: a pinned pipeline fails loudly instead of silently running the wrong model.
  So every slug is validated against `agy models` before it is used.
* When a model reports a quota/rate-limit error it goes into a cooldown. The chain is then
  walked from the top again, ending at the floor model (Gemini 3.8 Flash).
* The ledger is a plain JSON file so the routing decision is auditable after the fact.

CLI
---
    python3 model_router.py --discover          # show what is available and how it maps
    python3 model_router.py --pick build        # print the slug that would be used
    python3 model_router.py --status            # ledger summary
    python3 model_router.py --reset             # clear all cooldowns
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

ISO = "%Y-%m-%dT%H:%M:%S"

# Patterns that mean "this model is out of budget", matched case-insensitively
# against stderr and the error field of the JSON envelope.
LIMIT_PATTERNS = [
    r"quota",
    r"rate.?limit",
    r"exhaust",
    r"resource[_ ]exhausted",
    r"too many requests",
    r"\b429\b",
    r"limit reached",
    r"out of budget",
]

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_POLICY = HERE / "policy.yaml"
DEFAULT_LEDGER = HERE / "model_ledger.json"


class QuotaExhausted(RuntimeError):
    """Every model in the chain, including the floor, is cooling down."""

    def __init__(self, until: dt.datetime | None):
        self.until = until
        super().__init__(f"all models cooling down until {until.isoformat() if until else 'unknown'}")


def now() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


def _parse_yaml_minimal(text: str) -> dict:
    """
    Tiny YAML subset parser: nested maps, lists of scalars, scalars, comments.
    Enough for policy.yaml without a PyYAML dependency on a bare Arch box.
    """
    root: dict = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            val = line[2:].strip()
            if isinstance(parent, list):
                parent.append(val)
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            # could be a map or a list; peek is not worth it, create a dict and
            # convert to list on first "- " child
            child: dict | list = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            if val.startswith("[") and val.endswith("]"):
                parent[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
            else:
                parent[key] = val.strip("'\"")
    # convert empty dicts that received list children
    def fix(node):
        if isinstance(node, dict):
            for k, v in list(node.items()):
                node[k] = fix(v)
            return node
        return node
    return root


def load_policy(path: pathlib.Path) -> dict:
    text = path.read_text()
    try:  # prefer real YAML when available
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data or {}
    except Exception:
        return _parse_yaml_minimal(text)


def parse_models(output: str) -> dict[str, str]:
    """`agy models` prints '<slug>   <Label>' per line. Return {slug: label}."""
    models: dict[str, str] = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.lower().startswith(("model", "available", "─", "-")):
            continue
        parts = re.split(r"\s{2,}|\t+", line, maxsplit=1)
        slug = parts[0].strip()
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", slug):
            continue
        models[slug] = parts[1].strip() if len(parts) > 1 else ""
    return models


class Router:
    def __init__(self, policy_path=DEFAULT_POLICY, ledger_path=DEFAULT_LEDGER, agy="agy"):
        self.policy = load_policy(pathlib.Path(policy_path))
        self.ledger_path = pathlib.Path(ledger_path)
        self.agy = agy
        self._models: dict[str, str] | None = None

    # ---------- discovery ----------
    def models(self, refresh: bool = False) -> dict[str, str]:
        if self._models is not None and not refresh:
            return self._models
        try:
            out = subprocess.run(
                [self.agy, "models"], capture_output=True, text=True, timeout=60
            )
            self._models = parse_models(out.stdout or "")
        except Exception:
            self._models = {}
        return self._models

    # ---------- ledger ----------
    def ledger(self) -> dict:
        if self.ledger_path.exists():
            try:
                return json.loads(self.ledger_path.read_text())
            except json.JSONDecodeError:
                pass
        return {}

    def save_ledger(self, data: dict) -> None:
        self.ledger_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    def cooling(self, slug: str) -> bool:
        entry = self.ledger().get(slug, {})
        until = entry.get("cooldown_until")
        if not until:
            return False
        try:
            return dt.datetime.fromisoformat(until) > now()
        except ValueError:
            return False

    def earliest_expiry(self) -> dt.datetime | None:
        times = []
        for slug, entry in self.ledger().items():
            until = entry.get("cooldown_until")
            if until:
                try:
                    times.append(dt.datetime.fromisoformat(until))
                except ValueError:
                    pass
        return min(times) if times else None

    # ---------- selection ----------
    def chain(self, task_class: str) -> list[str]:
        chains = self.policy.get("chains") or {}
        chain = chains.get(task_class) or chains.get("build") or []
        if isinstance(chain, str):
            chain = [chain]
        floor = self.policy.get("floor_model")
        if floor and floor not in chain:
            chain = list(chain) + [floor]
        return list(chain)

    def pick(self, task_class: str) -> str:
        """First available, non-cooling model in the chain. Raises QuotaExhausted."""
        available = self.models()
        for slug in self.chain(task_class):
            if available and slug not in available:
                continue  # account does not expose it; skip quietly
            if not self.cooling(slug):
                return slug
        # Every model in the chain — the floor included, since chain() appends it —
        # is cooling. That is the end of an endless run: stop cleanly rather than
        # hammering a model that has no budget left.
        raise QuotaExhausted(self.earliest_expiry())

    def effort(self, task_class: str) -> str | None:
        return (self.policy.get("effort") or {}).get(task_class)

    # ---------- outcome ----------
    @staticmethod
    def is_limit_error(text: str) -> bool:
        low = (text or "").lower()
        return any(re.search(p, low) for p in LIMIT_PATTERNS)

    def record(self, slug: str, ok: bool, error_text: str = "") -> None:
        data = self.ledger()
        entry = data.setdefault(slug, {"runs": 0, "failures": 0})
        entry["runs"] = entry.get("runs", 0) + 1
        entry["last_used"] = now().isoformat()
        if not ok:
            entry["failures"] = entry.get("failures", 0) + 1
            if self.is_limit_error(error_text):
                minutes = int(
                    (self.policy.get("cooldown_minutes") or {}).get(
                        slug, (self.policy.get("cooldown_minutes") or {}).get("default", 300)
                    )
                )
                entry["cooldown_until"] = (now() + dt.timedelta(minutes=minutes)).isoformat()
                entry["cooldown_reason"] = (error_text or "")[:200]
                entry["exhausted_at"] = now().isoformat()
        else:
            entry.pop("cooldown_until", None)
            entry.pop("cooldown_reason", None)
        self.save_ledger(data)


# ---------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Model routing for the IoT-23 autopilot")
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--agy", default=os.environ.get("AGY_BIN", "agy"))
    ap.add_argument("--discover", action="store_true", help="list available models and chain mapping")
    ap.add_argument("--pick", metavar="TASK", help="print the model that would be chosen")
    ap.add_argument("--status", action="store_true", help="print the ledger")
    ap.add_argument("--reset", action="store_true", help="clear all cooldowns")
    args = ap.parse_args(argv)

    router = Router(args.policy, args.ledger, args.agy)

    if args.reset:
        data = router.ledger()
        for entry in data.values():
            entry.pop("cooldown_until", None)
            entry.pop("cooldown_reason", None)
        router.save_ledger(data)
        print("cooldowns cleared")
        return 0

    if args.status:
        print(json.dumps(router.ledger(), indent=2, sort_keys=True))
        return 0

    if args.discover:
        models = router.models(refresh=True)
        if not models:
            print("could not read `agy models` — is the CLI authenticated?", file=sys.stderr)
            return 1
        print(f"{len(models)} models available\n")
        for slug, label in sorted(models.items()):
            mark = "COOLING" if router.cooling(slug) else ""
            print(f"  {slug:34} {label:34} {mark}")
        print("\nchain mapping")
        for task in (router.policy.get("chains") or {}):
            print(f"  {task:12} -> {router.chain(task)}")
        print(f"\nfloor: {router.policy.get('floor_model')}")
        return 0

    if args.pick:
        try:
            slug = router.pick(args.pick)
        except QuotaExhausted as exc:
            print(f"EXHAUSTED: {exc}", file=sys.stderr)
            return 3
        print(slug)
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
