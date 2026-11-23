# Installing the agent layer

Drop these files into the root of `IDP-LOCAL` and Antigravity picks them up automatically.

## 1. Copy into the repo

```bash
cd /home/harish/IDP-LOCAL
unzip -o ~/Downloads/IDP-LOCAL-agents.zip -d .
ls -la AGENTS.md .agents/
```

Resulting tree:

```
IDP-LOCAL/
├── AGENTS.md                      # always-on project rules
├── KAGGLE-COMPUTE.md              # architecture and one-time setup
├── .agents/
│   ├── agents/
│   │   ├── manager.md
│   │   ├── data-engineer.md
│   │   └── tester.md
│   ├── rules/
│   │   ├── data-safety.md         # always_on
│   │   ├── kaggle-compute.md      # always_on
│   │   ├── stage-gate.md          # model_decision
│   │   └── python-conventions.md  # glob: *.py, *.ipynb
│   └── skills/
│       ├── kaggle-run/SKILL.md    (+ scripts/kaggle_run.sh)
│       ├── stage-gate/SKILL.md
│       └── obsidian-sync/SKILL.md (+ scripts/sync_brain.sh)
├── .github/
│   ├── CODEOWNERS
│   └── pull_request_template.md
└── notebooks/
    └── kernel-metadata.template.json
```

## 2. Verify discovery

```bash
cd /home/harish/IDP-LOCAL
agy                       # start once in this folder and accept the trust prompt
```

Inside the TUI:

- `/agents` — manager, data-engineer and tester should be listed
- `/kaggle-run`, `/stage-gate`, `/obsidian-sync` — the skills appear as slash commands
- `/skills reload` if you added a skill while the CLI was already running

If an agent does not appear, the cause is almost always a frontmatter problem — Antigravity **silently skips** a file whose YAML is invalid or whose `model` value is not one of `inherit`, `flash_lite`, `flash`, `pro`. Check with `agy agents` too.

## 3. Set the paths

Defaults assume:

- repo: `/home/harish/IDP-LOCAL`
- vault: `/home/harish/obsidian/IoT23 Dataset`

If yours differ, export the overrides in your shell profile:

```bash
export IDP_REPO="/home/harish/IDP-LOCAL"
export IDP_VAULT="/home/harish/obsidian/IoT23 Dataset"
```

## 4. Link the vault

```bash
bash .agents/skills/obsidian-sync/scripts/sync_brain.sh
```

## 5. Add the process docs

The five documents from the previous round go into `docs/`, where the rules already point:

```bash
mkdir -p docs
# place these at the paths shown
#   docs/build-guide.md      (the process: stages, gates, PR flow)
#   docs/manager.md          (human-readable role card)
#   docs/data-engineer.md
#   docs/tester.md
```

They remain the source of truth for **process**. The agent files in `.agents/agents/` are the executable version of the same roles — same rules, written for an agent instead of a person. When one changes, change the other in the same PR.

## 6. Tool allowlists

Each agent declares a `tools` allowlist. The names used here are the documented built-ins:

| Tool | Used by | Purpose |
|---|---|---|
| `view_file` | all | read files |
| `grep_search` | all | search the repo |
| `run_command` | all | git, gh, kaggle, pytest |
| `replace_file_content` | data-engineer | edit code |
| `manage_task` | manager, data-engineer | track multi-step work |
| `search_web`, `read_url_content` | tester | check Zeek/Kaggle documentation |

A misspelled tool name can make a subagent hang rather than fail cleanly, so if you add one, verify it first with `agy agents` and a single trivial task.

The manager and tester deliberately have **no** `replace_file_content`: they can read and run, but they cannot edit the pipeline. That is what keeps the two-key rule real.

## 7. First run

```bash
agy
> /agents            # pick data-engineer
> Read docs/build-guide.md §5.2 for Stage 0, then create the branch
  stage/00-definition and write the stage note skeleton.
```

Then switch to `/agents` → manager to assign, and tester when the PR is up.

## 8. What this bundle does not contain

- The dataset. It lives on Kaggle.
- `src/iot23/`. The data-engineer writes it, stage by stage.
- `docs/`. Copy the five process documents in, as above.
- `kaggle.json`. Never in a repository.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Agents missing from `/agents` | invalid YAML frontmatter, or `model` not a valid tier |
| Skills missing from slash commands | missing `name`/`description` in `SKILL.md`, or wrong folder depth |
| Rules not applied | `.agents/rules/*.md` needs frontmatter with a valid `trigger`; invalid files are discarded silently |
| Agent hangs on a task | a tool name in its `tools` list is not a real built-in |
| Nothing loads at all | you are outside the repo root; discovery stops at the git root and does not search subfolders |
