from langchain_core.tools import tool
from os import getenv
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict, Sequence
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, BaseMessage, AIMessage, HumanMessage
from dotenv import load_dotenv
import requests

load_dotenv()


llm = ChatOpenAI(
    openai_api_key=getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="google/gemini-2.0-flash-001",
    temperature=0.2
)


@tool
def usd_to_cop_converter(usd_amount: float) -> float:
    """Call to convert USD to COP using the latest exchange rate"""
    response = requests.get(
        'https://run.mocky.io/v3/8c3db615-027d-4883-8327-6a3724d4b749')

    json_response = response.json()

    return {
        'exchange_rate': json_response,
        'conversion': usd_amount * json_response['rate']
    }


tools = [usd_to_cop_converter]

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)

agent_system_prompt = SystemMessage(
    content="""
    You are an expert currencies converter AI agent that
    uses tools when necessary to help the user.
    """)


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def chatbot(state: State):
    ai_response = llm_with_tools.invoke(
        [agent_system_prompt, *state["messages"]])

    return {
        "messages": [ai_response]
    }


def router(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """

    messages = state.get("messages", [])
    last_message = messages[-1]

    # Is the last message trying to call a tool?
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"

    return END


graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# Edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot", router, ["tools", END])
graph_builder.add_edge("tools", "chatbot")

agent = graph_builder.compile()
