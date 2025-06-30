from datetime import datetime
from typing import Literal

from langchain.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

from agents.llama_guard import LlamaGuard, LlamaGuardOutput, SafetyAssessment
from core import get_model, settings
from data_products.customer_360 import Customer360
from data_products.deals_360 import Deals360
from data_products.inventory_360 import Inventory360
from data_products.proposals_360 import Proposals360
from data_products.reorder_360 import Reorder360


class OrderState(MessagesState, total=False):
    """`total=False` is PEP589 specs.

    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    safety: LlamaGuardOutput
    remaining_steps: RemainingSteps


class OrderHistoryTool(BaseTool):
    name: str = "order_history"
    description: str = "Get the customer's order history"

    async def _arun(self, query: str) -> str:
        # Implement actual database query here
        reorder_360 = Reorder360()
        customer_id = "011a94f0-35ce-4dcc-ab54-5f693123e74f"
        results = reorder_360.get_reorder_patterns(customer_id=customer_id)
        return str(results)

    def _run(self, query: str) -> str:
        raise NotImplementedError("OrderHistoryTool only supports async operations")


class Customer360Tool(BaseTool):
    name: str = "customer_360"
    description: str = "Get comprehensive customer information including status, account standing, and delivery preferences"

    async def _arun(self, query: str) -> str:
        # Implement actual customer status check
        customer_360 = Customer360()
        customer_id = "011a94f0-35ce-4dcc-ab54-5f693123e74f"
        results = customer_360.get_customer_status(customer_id=customer_id)
        return str(results)

    def _run(self, query: str) -> str:
        raise NotImplementedError("Customer360Tool only supports async operations")


class ReorderAnalysisTool(BaseTool):
    name: str = "reorder_analysis"
    description: str = "Analyze customer's order patterns and history to provide insights"

    async def _arun(self, query: str) -> str:
        # Implement reorder pattern analysis
        reorder_360 = Reorder360()
        customer_id = "011a94f0-35ce-4dcc-ab54-5f693123e74f"
        results = reorder_360.get_reorder_patterns(customer_id=customer_id)
        return str(results)

    def _run(self, query: str) -> str:
        raise NotImplementedError("ReorderAnalysisTool only supports async operations")


class ProductIds(BaseModel):
    product_ids: list[str] = Field(description="A list of product ids to check the availability of")


class Product360Tool(BaseTool):
    name: str = "product_360"
    description: str = (
        "Check the availability of input product ids, stock levels, and alternative products"
    )
    args_schema: type[BaseModel] = ProductIds

    async def _arun(self, product_ids: list[str]) -> str:
        # Implement product availability and alternatives check
        inventory_360 = Inventory360()
        # customer_id = "011a94f0-35ce-4dcc-ab54-5f693123e74f"
        results = inventory_360.get_stock_levels(product_ids)
        return str(results)

    def _run(self, query: str) -> str:
        raise NotImplementedError("Product360Tool only supports async operations")


class Deals360Tool(BaseTool):
    name: str = "deals_360"
    description: str = "Find current deals, discounts, and special offers"

    async def _arun(self, query: str) -> str:
        deals_360 = Deals360()
        customer_id = "011a94f0-35ce-4dcc-ab54-5f693123e74f"
        results = deals_360.get_active_deals(customer_id=customer_id)
        return str(results)

    def _run(self, query: str) -> str:
        raise NotImplementedError("Deals360Tool only supports async operations")


class Proposals360Tool(BaseTool):
    name: str = "proposals_360"
    description: str = "Get personalized product recommendations and suggestions"

    async def _arun(self, query: str) -> str:
        proposals_360 = Proposals360()
        customer_id = "011a94f0-35ce-4dcc-ab54-5f693123e74f"
        results = proposals_360.get_recommendations(customer_id=customer_id)
        return str(results)

    def _run(self, query: str) -> str:
        raise NotImplementedError("Proposals360Tool only supports async operations")


customer_360 = Customer360Tool()
reorder_analysis = ReorderAnalysisTool()
product_360 = Product360Tool()
deals_360 = Deals360Tool()
proposals_360 = Proposals360Tool()

tools = [customer_360, reorder_analysis, product_360, deals_360, proposals_360]


current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
You are an intelligent order assistant that helps customers place orders following a specific process:

1. First, verify the customer's standing and status
2. Analyze their reorder patterns to make informed suggestions, take user's input before moving forward.
3. Check product availability for suggested items
4. Propose alternatives for unavailable products
5. Look for applicable deals and volume discounts
6. Suggest new products they might be interested in
7. Discuss delivery timing
8. Finalize the order

Guidelines:
- Always check customer status before proceeding with suggestions
- Be transparent about product availability
- Highlight savings opportunities
- Make personalized recommendations
- Confirm all details before finalizing
- Current date: {current_date}
    """


def wrap_model(model: BaseChatModel) -> RunnableSerializable[OrderState, AIMessage]:
    bound_model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | bound_model  # type: ignore[return-value]


def format_safety_message(safety: LlamaGuardOutput) -> AIMessage:
    content = (
        f"This conversation was flagged for unsafe content: {', '.join(safety.unsafe_categories)}"
    )
    return AIMessage(content=content)


async def acall_model(state: OrderState, config: RunnableConfig) -> OrderState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # Run llama guard check here to avoid returning the message if it's unsafe
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("Agent", state["messages"] + [response])
    if safety_output.safety_assessment == SafetyAssessment.UNSAFE:
        return {"messages": [format_safety_message(safety_output)], "safety": safety_output}

    if state["remaining_steps"] < 2 and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, need more steps to process this request.",
                )
            ]
        }
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


async def llama_guard_input(state: OrderState, config: RunnableConfig) -> OrderState:
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("User", state["messages"])
    return {"safety": safety_output, "messages": []}


async def block_unsafe_content(state: OrderState, config: RunnableConfig) -> OrderState:
    safety: LlamaGuardOutput = state["safety"]
    return {"messages": [format_safety_message(safety)]}


# Define the graph
agent = StateGraph(OrderState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("guard_input", llama_guard_input)
agent.add_node("block_unsafe_content", block_unsafe_content)
agent.set_entry_point("guard_input")


# Check for unsafe input and block further processing if found
def check_safety(state: OrderState) -> Literal["unsafe", "safe"]:
    safety: LlamaGuardOutput = state["safety"]
    return "safe"
    match safety.safety_assessment:
        case SafetyAssessment.UNSAFE:
            return "unsafe"
        case _:
            return "safe"


agent.add_conditional_edges(
    "guard_input", check_safety, {"unsafe": "block_unsafe_content", "safe": "model"}
)

# Always END after blocking unsafe content
agent.add_edge("block_unsafe_content", END)

# Always run "model" after "tools"
agent.add_edge("tools", "model")


# After "model", if there are tool calls, run "tools". Otherwise END.
def pending_tool_calls(state: OrderState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})


order_assistant_new = agent.compile(checkpointer=MemorySaver(), store=InMemoryStore())
