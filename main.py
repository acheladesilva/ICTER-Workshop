"""CLI: route a task to one or all of the agent scenarios."""

import argparse
import os

from dotenv import load_dotenv

from scenarios import DEFAULT_MODEL, TASKS

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph agent tutorial")
    parser.add_argument("task", choices=TASKS)
    parser.add_argument("--scenario", help="run only one scenario of the task")
    parser.add_argument(
        "--model",
        default=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        help="OpenRouter model id (must support tool calling)",
    )
    args = parser.parse_args()

    task = TASKS[args.task]
    question, scenarios = task.QUESTION, task.SCENARIOS
    if args.scenario and args.scenario not in scenarios:
        parser.error(f"scenario must be one of: {', '.join(scenarios)}")
    names = [args.scenario] if args.scenario else list(scenarios)
    for name in names:
        print(f"\n=== {name} ===")
        print(scenarios[name](question, args.model))


if __name__ == "__main__":
    main()
