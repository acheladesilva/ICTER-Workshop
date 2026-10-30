# τ² telecom workshop

One customer problem, four conditions: **“My mobile internet is broken or slow;
I need excellent speed, and I have no Wi-Fi.”** John Smith uses `555-123-2002`.
The support agent controls the account; a separate simulated user controls the
phone. Students see their conversation and the actual environment checks.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
uv sync --frozen
cp .env.example .env  # first setup only; add OPENROUTER_API_KEY inside .env
uv run telecom.py validate  # offline solvability check
uv run telecom.py easy
```

The Python version and Tau dependency are configured locally; no separate Tau
checkout is needed. The key stays in ignored `.env`.

Both participants use **`nvidia/nemotron-3.5-lightning:free`** by default. The
telecom runner rejects paid models/nonzero catalog prices and sets zero-price
provider limits. There is no paid fallback. `--model` accepts another free model;
free-provider outages are reported as errors, separately from task failures.

## Four tasks

The goal, baseline agent prompt, policy and tools stay the same. Only the user
persona and initial faults/checks change.

| Task | Main scenario | Environment checks required to pass |
|---|---|---|
| `easy` | Cooperative user. Airplane mode is on; network preference is stuck on 2G. | Mobile data works; speed ≥200 Mbps rated **Excellent**; airplane mode off; cellular service connected. **4 checks.** |
| `hard-user` | Same two faults. An anxious, terse user refuses multi-step requests and may leave after repeated overload. | The same **4 checks** as `easy`. |
| `hard-env` | Cooperative user. Adds mobile data disabled, Data Saver enabled, a faulty VPN and exhausted data allowance. | All 4 easy checks, plus Data Saver off, allowance no longer exceeded, and **exactly 2 GB** added to account `C1001`, line `L1002`. **7 checks.** |
| `hard-both` | Difficult user with all six faults. The agent must retain cooperation while completing every repair. | The same **7 checks** as `hard-env`. |

Run `uv run telecom.py <task>` or `uv run telecom.py all`. Each starts fresh with
a 12-round limit (`--max-turns` changes it). The speed check also catches an
unresolved VPN or slow network mode. The user can approve a 2 GB top-up but does
not want a plan change. All telecom charges and phone changes are simulated.

## Watch the conversation

Runs print the dialogue automatically. In a second terminal:

```bash
uv run showprogress.py --follow         # follow the latest run
uv run showprogress.py --follow --tools # include tool calls and results
```

Replay the tested examples **without an API key or model calls**:

```bash
uv run showprogress.py examples/easy.jsonl
uv run showprogress.py examples/hard-user.jsonl
uv run showprogress.py examples/hard-env.jsonl
uv run showprogress.py examples/hard-both.jsonl
```

Add `--delay 1` for a paced replay or `--tools` to inspect actions. New traces,
prompt snapshots and results are saved in ignored `runs/`.

## Live-tested results — 30 October 2026

| Condition | Result | Teaching point |
|---|---|---|
| Easy | **PASS, 4/4** | Agent instructions lead to real user actions and restored speed. |
| Hard user | **FAIL, 0/4** | Repeated checklists overwhelm the user, who leaves. |
| Hard environment | **FAIL, 5/7** | Repeated top-ups add 296 GB instead of 2 GB; speed remains unresolved. The tool-step limit stops the loop. |
| Both hard | **FAIL, 0/7** | The user leaves after repeated overload, before the six faults are repaired. |

All 67 selected model replies reported zero API cost. These are selected teaching
recordings; fresh runs can differ. The full attempt history, including excluded
errors, is in `examples/manifest.json`. **The three improvements are left for our
next session**; no improved agent is supplied. Later, copy
`workshop/prompts/baseline.txt` to `my-agent.txt` and use `--agent-prompt my-agent.txt`.

## Source and verification

This adapts [Sierra τ²-bench](https://github.com/sierra-research/tau2-bench)'s native
telecom environment, tasks, tools and assertions using a LangGraph runner.
It is not an official benchmark score. The hard user combines Tau's Hard persona
with a workshop rule: two overloaded phone requests trigger departure; a clear
single-step request resets patience. The shared opening and departure are marked
as scripted. Success requires actual state checks, not a model's claim.

```bash
uv run python -m unittest discover -s tests -v
uv run python scripts/verify_examples.py
```

The verifier replays native tool calls and reproduces all four grades offline.
See [instructor notes](docs/telecom-details.md) for the exact persona rule, source
tasks, limitations and file map. The original tutorial remains available through
`main.py`; see [its instructions](docs/original-tutorial.md).
