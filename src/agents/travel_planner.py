from datetime import datetime
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode
from langgraph.store.memory import InMemoryStore

from agents.tools import BookFlightTool, SearchFlightsTool, update_state
from core import get_model, settings

# langfuse_handler = CallbackHandler(
#     public_key="pk-lf-82d093de-555c-4f58-9bea-b7431ef0a95c",
#     secret_key="sk-lf-08629fd5-04cc-42de-bfca-d69288f833f7",
#     host="https://cloud.langfuse.com",
# )


class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    remaining_steps: RemainingSteps
    budget: str | None
    flight_number: str | None
    hotel_id: str | None
    no_of_adults: int | None
    no_of_children: int | None
    travel_class: str | None
    is_one_way: bool | None
    check_in: str | None
    check_out: str | None
    origin: str | None
    destination: str | None


tools = [SearchFlightsTool(), BookFlightTool(), update_state]

current_date = datetime.now().strftime("%Y-%m-%d")
instructions = f"""
You are a travel assistant. You can search for flights and hotels, book them, and ask the user for more information if needed. You can also end the conversation if the user is done.

You are provided with tools:
- SearchFlightsTool: Search for flights based on user input. Also list them if found. In the origin and destination, dont put the IATA code, but the city name.
- BookFlightTool: Book a flight using the provided details.
- update_state: Update the state of the trip parameters and verify them with the user.

Notes:
- You have to ask the user for the following information:full name, date of birth, phone number, gender, seat preference, meal preference, special assistance, payment method. Only when you have all the information, you can book the flight.
- Always convert DD-MM-YYYY format to YYYY-MM-DD.
- Ask for missing information if needed.
- If a flight can't be found, say so.
- If unsure, say "I don't know".
- Call the update_state tool only after BookFlightTool is called
- Today's date is {current_date}.
"""


def wrap_model(model) -> RunnableSerializable[AgentState, AIMessage]:
    bound_model = model.bind_tools(tools)
    prepend_instruction = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"]
    )
    return prepend_instruction | bound_model


async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    print(config["configurable"].get("model", settings.DEFAULT_MODEL))
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    runnable = wrap_model(m)

    # config["callbacks"] = [config["callbacks"], langfuse_handler]
    # print(config["callbacks"])
    # result = await runnable.ainvoke(state, config={"callbacks": [langfuse_handler]})
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
    return {"messages": [result]}


def has_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "done"


agent = StateGraph(AgentState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))

agent.set_entry_point("model")

agent.add_conditional_edges("model", has_tool_calls, {"tools": "tools", "done": END})
agent.add_edge("tools", "model")

travel_planner = agent.compile(checkpointer=MemorySaver(), store=InMemoryStore())
