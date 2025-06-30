from dataclasses import dataclass

from langgraph.pregel import Pregel

from agents.order_assistant import order_assistant
from agents.order_assistant_new import order_assistant_new

# from agents.bg_task_agent.bg_task_agent import bg_task_agent
# from agents.chatbot import chatbot
# from agents.command_agent import command_agent
# from agents.interrupt_agent import interrupt_agent
# from agents.knowledge_base_agent import kb_agent
# from agents.langgraph_supervisor_agent import langgraph_supervisor_agent
# from agents.multi_agent_travel_planner import supervisor
from agents.rag_assistant import rag_assistant
from agents.research_assistant import research_assistant

# from agents.supervisor_travel import supervisor_travel
# from agents.travel_planner import travel_planner
from agents.travel_agent_support import workflow
from schema import AgentInfo

DEFAULT_AGENT = "order-assistant"


@dataclass
class Agent:
    description: str
    graph: Pregel


agents: dict[str, Agent] = {
    "travel-agent-support": Agent(
        description="A multi-agent travel planner.",
        graph=workflow,
    ),
    "order-assistant": Agent(
        description="An order assistant that can handle orders and inventory.",
        graph=order_assistant_new,
    ),
    # "supervisor-travel": Agent(
    #     description="A multi-agent travel planner.",
    #     graph=supervisor_travel,
    # ),
    # "multi-agent-travel-planner": Agent(
    #     description="A multi-agent travel planner.",
    #     graph=supervisor,
    # ),
    # # "travel-planner": Agent(description="A travel planner agent.", graph=travel_planner),
    # "chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    "research-assistant": Agent(
        description="A research assistant with web search and calculator.", graph=research_assistant
    ),
    "rag-assistant": Agent(
        description="A RAG assistant with access to information in a database.", graph=rag_assistant
    ),
    # "command-agent": Agent(description="A command agent.", graph=command_agent),
    # "bg-task-agent": Agent(description="A background task agent.", graph=bg_task_agent),
    # "langgraph-supervisor-agent": Agent(
    #     description="A langgraph supervisor agent", graph=langgraph_supervisor_agent
    # ),
    # "interrupt-agent": Agent(description="An agent the uses interrupts.", graph=interrupt_agent),
    # "knowledge-base-agent": Agent(
    #     description="A retrieval-augmented generation agent using Amazon Bedrock Knowledge Base",
    #     graph=kb_agent,
    # ),
}


def get_agent(agent_id: str) -> Pregel:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]
