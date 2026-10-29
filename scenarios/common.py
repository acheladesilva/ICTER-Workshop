"""Shared model setup, mock user data and the ask helper."""

import os

from langchain_openai import ChatOpenAI
from loguru import logger

from .observability import trace

DEFAULT_MODEL = "openrouter/free"

USER = {"name": "Alex Perera", "account_id": "ACC-1001", "account_type": "savings"}
USER_CONTEXT = (
    "You are a banking assistant. The current user is "
    f"{USER['name']} (account {USER['account_id']}, {USER['account_type']})."
)

MOCK_BALANCES = {"ACC-1001": 2450.75}


def make_model(name: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=name,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )


def ask(agent, question: str, config: dict | None = None) -> str:
    """Run one turn. The trace handler prints and logs every step."""
    config = {**(config or {}), "callbacks": [trace]}
    result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
    answer = result["messages"][-1].text
    logger.info("final answer: {}", answer)
    return answer
