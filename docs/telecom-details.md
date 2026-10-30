# Instructor notes: telecom adaptation

## Source and boundary

The native telecom environment, tools, policies, assertions, Easy/Hard personas
and source tasks come from [Sierra τ²-bench](https://github.com/sierra-research/tau2-bench),
commit `363133ada1936491fb5bcec33cd62c3518a99f65`.

The two source task IDs are:

- `[mobile_data_issue]airplane_mode_on|bad_network_preference[PERSONA:Hard]`
- `[mobile_data_issue]airplane_mode_on|bad_network_preference|bad_vpn|data_mode_off|data_saver_mode_on|data_usage_exceeded[PERSONA:Hard]`

Their unmodified records are in `workshop/data/source_tasks.json`. The workshop
swaps the persona independently of the environment, giving a 2×2 comparison with
the same goal. All four initially fail at least one check; upstream reference
actions satisfy every check. `telecom.py validate` verifies this offline.

This is a **custom LangGraph harness**, not the official Tau orchestrator or a
leaderboard evaluation. Package initializers were reduced to avoid installing
the unrelated benchmark/voice stack; native telecom modules are unchanged.
See `vendor/tau2-core/PROVENANCE.json` for hashes and the included MIT license.

The support model receives the same baseline prompt, native policy and tool
catalog in every condition. The customer receives its scenario and persona.
Neither sees initialization actions, reference solutions or grading assertions.
The support model has account tools; only the customer has phone tools.
`ask_customer` lists the phone tools requested in that support turn. The runner
offers those tools to the customer without executing them automatically.
This prevents a weak simulator from independently solving the task.

The initial greeting and customer request are scripted and identical across
conditions. Subsequent dialogue and tool choices come from the two model roles,
except the conditional departure described below. Histories are separate, while
the native telecom state is shared.

## Hard user

Tau's native Hard persona describes an anxious, inexperienced older customer.
It does **not** itself implement the text-conversation hang-up behavior used here.
We combine it with native minimal verbosity and an explicit workshop addition:

1. A request offering more than one distinct phone tool overwhelms the user.
   The user takes no action and is prompted to ask for one clear step.
2. A second such request, without a single-tool request between them, triggers
   the saved scripted departure. Ordinary conversation does not reset patience.
3. A single-tool request resets patience and allows the user to act normally.

The rule is based on the structured request, not an unreliable count of words
in the dialogue. Leaving is conditional on agent behavior. The hard task remains
solvable through clear instructions; success is not disabled in code.

## What the checks mean

Easy checks require working mobile data, speed at least 200 Mbps rated Excellent,
airplane mode off and service connected. Hard checks add Data Saver off, allowance
not exceeded and exactly 2 GB refueled on account C1001, line L1002. The speed
requirement also catches a bad VPN or slow network preference.

These are native state assertions. They do not independently grade every policy
rule, consent wording or conversation quality. A model claiming success never
overwrites the state. Tool-step/turn limits bound a run; provider/protocol errors
and interrupted runs are labeled ERROR, not task failures.

## Recorded evidence

`examples/manifest.json` lists four selected recordings and all 17 development
attempts. Every raw trace and available prompt/task/result snapshot is retained
under `examples/attempts/`. Selected traces are exact copies, not edited scripts.

The four selected runs used the same model and identical agent prompt. They have
67 successful model replies, all reporting zero cost. Across all retained
attempts, 237 successful replies report zero cost. These are model-response cost
reports, not an independent billing audit.

Earlier development included free-provider capacity errors, interrupted runs,
malformed output, and a pilot where the customer self-solved before request gating.
These are excluded as classroom baseline evidence. One earlier combined trace
recorded FAIL despite malformed customer markup; its manifest explicitly excludes
it. The final runner detects that condition as ERROR.

Run code hashes can differ because protocol-error detection, documentation and
trace-write ordering were corrected during development. Final maintenance also
ensures a tool-step limit still passes if every state check is already satisfied;
none of the selected grades changes. Actual prompt hashes and
task definitions are saved. Some simultaneous callbacks in the original hard-env
recording flushed out of order; recorded `seq` numbers preserve their order.
The verifier sorts by that sequence and reproduces **every tool result and final
check**. New writes are serialized. Raw historical files remain unchanged.

Free models may repeat instructions, confuse customer/support roles or emit
invalid tool output. The recordings preserve those imperfections. They are
selected classroom cases, not controlled success-rate estimates, and a fresh
live attempt can behave differently. Use replays for a predictable demonstration.

## Later exercise

The failed variants intentionally have no improved agent. Keep the scenario,
checks and user fixed while changing `workshop/prompts/baseline.txt` via a copied
`--agent-prompt` file. Compare the conversation and tool trace, then inspect the
same final assertions. Useful discussion points are clear instructions, verifying
the actual speed, and preventing repeated account writes. Implement and test
those improvements with the instructor in the next session.

## File map

| File | Purpose |
|---|---|
| `telecom.py` | Run one condition, all four, or offline solvability validation. |
| `workshop/tasks.py` | Load native source tasks, swap personas and add native assertions. |
| `workshop/runner.py` | Alternate the two agents, constrain tool ownership and grade state. |
| `workshop/models.py` | Enforce free-only OpenRouter models and retry transient HTTP errors. |
| `workshop/prompts/baseline.txt` | Unimproved starting support-agent prompt. |
| `workshop/prompts/hard_user_addition.txt` | Workshop patience rule layered onto the native persona. |
| `workshop/trace.py`, `showprogress.py` | Record, display, replay and follow terminal conversations. |
| `tests/test_workshop.py` | Offline scenario, protocol, tool-ownership and grading checks. |
| `scripts/verify_examples.py` | Independently replay saved native calls and check recorded outcomes. |
| `examples/` | Selected recordings, their snapshots and the complete attempt archive. |
| `vendor/tau2-core/` | Bundled native modules, license and source hashes. |
