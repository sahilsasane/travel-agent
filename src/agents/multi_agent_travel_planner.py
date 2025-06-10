from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import InjectedState, ToolNode
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from agents.travel_agents import book_flights_agent, search_flights_agent
from core import get_model, settings


class SupervisorState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    remaining_steps: RemainingSteps


agents = [search_flights_agent, book_flights_agent]

instructions = (
    "You are a supervisor managing two agents:\n"
    "1. A flight search agent that assists users in finding flights based on their travel preferences.\n"
    "2. A flight booking agent that assists users in booking flights based on their travel preferences.\n"
    "You will receive updates from both agents and you need to ensure that they are working together effectively.\n"
)

# Supervisor agent scratch


def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )

    return handoff_tool


assign_to_search_agent = create_handoff_tool(
    agent_name="search_flights_agent",
    description="Assign task to a flights search agent.",
)

assign_to_book_agent = create_handoff_tool(
    agent_name="book_flights_agent",
    description="Assign task to a flights booking agent.",
)

tools = [assign_to_search_agent, assign_to_book_agent]


def wrap_model(model) -> RunnableSerializable[SupervisorState, AIMessage]:
    bound_model = model.bind_tools(tools)
    prepend_instruction = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"]
    )
    return prepend_instruction | bound_model


async def acall_model(state: SupervisorState, config: RunnableConfig) -> SupervisorState:
    print(config["configurable"].get("model", settings.DEFAULT_MODEL))
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    runnable = wrap_model(m)

    # print(config["callbacks"])
    # result = await runnable.ainvoke(state, config={"callbacks": [langfuse_handler]})
    # result = await runnable.ainvoke(state, config)
    # result = runnable.astream(state, config)
    accumulated_content = ""
    final_chunk = None
    tool_calls = []

    async for chunk in runnable.astream(state, config):
        final_chunk = chunk  # Keep the last chunk for metadata
        if chunk.content:
            accumulated_content += chunk.content
        if hasattr(chunk, "tool_calls") and chunk.tool_calls:
            tool_calls.extend(chunk.tool_calls)

    # Create final AIMessage with accumulated content
    if final_chunk:
        result = AIMessage(
            content=accumulated_content,
            id=final_chunk.id,
            tool_calls=tool_calls,
            additional_kwargs=final_chunk.additional_kwargs,
            response_metadata=final_chunk.response_metadata,
        )
    else:
        # Fallback if no chunks received
        result = await runnable.ainvoke(state, config)

    if state["remaining_steps"] < 2 and result.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=result.id,
                    content="Sorry, need more steps to process this request.",
                )
            ]
        }
    return {"messages": result}


def has_tool_calls(state: SupervisorState) -> Literal["tools", "done"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "done"


# Handoffs

graph = StateGraph(SupervisorState)
graph.add_node("model", acall_model)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("model")

graph.add_conditional_edges("model", has_tool_calls, {"tools": "tools", "done": END})
graph.add_edge("tools", "model")

supervisor_agent = graph.compile(
    checkpointer=MemorySaver(), store=InMemoryStore(), name="supervisor"
)


# add helper agents
supervisor = (
    StateGraph(MessagesState)
    .add_node(supervisor_agent, destinations=("search_flights_agent", "book_flights_agent", END))
    .add_node(search_flights_agent)
    .add_node(book_flights_agent)
    .add_edge(START, "supervisor")
    .add_edge("search_flights_agent", "supervisor")
    .add_edge("book_flights_agent", "supervisor")
    .compile(checkpointer=MemorySaver(), store=InMemoryStore())
)
