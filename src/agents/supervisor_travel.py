from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from langgraph_supervisor import create_supervisor

from agents.travel_agents import book_flights_agent, search_flights_agent
from core import get_model, settings

model = get_model(settings.DEFAULT_MODEL)


class SupervisorState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    remaining_steps: RemainingSteps


supervisor_travel = create_supervisor(
    model=model,
    state_schema=SupervisorState,
    agents=[search_flights_agent, book_flights_agent],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "1. A flight search agent that assists users in finding flights based on their travel preferences.\n"
        "2. A flight booking agent that assists users in booking flights based on their travel preferences.\n"
        "You will receive updates from both agents and you need to ensure that they are working together effectively.\n"
        "Whenever a query about booking is received, you should have at least transferred it to search_flights_agent to get the flight options before transferring to book_flights_agent.\n"
    ),
    add_handoff_back_messages=True,
    # output_mode="full_history",
).compile(checkpointer=MemorySaver())
