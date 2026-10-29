"""CLI: route a task to one or all of the agent scenarios."""

from enum import Enum
from typing import Annotated

import typer
from dotenv import load_dotenv

from scenarios import DEFAULT_MODEL, TASKS

load_dotenv()

Task = Enum("Task", {name: name for name in TASKS}, type=str)


def main(
    task: Annotated[Task, typer.Argument(help="Task to run")],
    scenario: Annotated[
        str | None, typer.Option(help="Run only one scenario of the task")
    ] = None,
    model: Annotated[
        str,
        typer.Option(
            envvar="OPENROUTER_MODEL",
            help="OpenRouter model id (must support tool calling)",
        ),
    ] = DEFAULT_MODEL,
) -> None:
    module = TASKS[task.value]
    scenarios = module.SCENARIOS
    if scenario and scenario not in scenarios:
        raise typer.BadParameter(
            f"must be one of: {', '.join(scenarios)}", param_hint="--scenario"
        )
    for name in [scenario] if scenario else scenarios:
        typer.echo(f"\n=== {name} ===")
        typer.echo(scenarios[name](module.QUESTION, model))


if __name__ == "__main__":
    typer.run(main)
