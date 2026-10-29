"""CLI: route a task to one or all of the agent scenarios."""

from enum import Enum
from typing import Annotated

import typer
from dotenv import load_dotenv

from loguru import logger
from rich.panel import Panel

from scenarios import DEFAULT_MODEL, TASKS
from scenarios.observability import console, setup_logging, trace

load_dotenv()
setup_logging()

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
        trace.reset()
        logger.info("start {} / {} (model {})", task.value, name, model)
        console.print()
        console.rule(f"[bold]{task.value} / {name}[/bold]")
        console.print(Panel(module.QUESTION, title="task", border_style="green"))
        outcome = scenarios[name](module.QUESTION, model)
        if outcome:
            console.print(Panel(outcome, title="outcome", border_style="bold white"))
        logger.info("end {} / {}: {}", task.value, name, outcome)


if __name__ == "__main__":
    typer.run(main)
