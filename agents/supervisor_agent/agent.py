from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage
from agents.scraper_agent.agent import agent as ScraperAgent
from agents.data_analyst_agent.agent import agent as DataAnalystAgent
from agents.currency_converter_agent.agent import agent as CurrencyConverterAgent
import json

load_dotenv()


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: Literal["data_analyst", "scraper",
                  "currency_converter", "FINISH"]
    task: str


llm = ChatOpenAI(
    openai_api_key=getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openai/gpt-4o-2024-11-20",
    temperature=0
)

workers = [
    "data_analyst",
    "scraper",
    "currency_converter"
]

FINISH_COMMAND = "FINISH"


class SupervisorDecision(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal["data_analyst", "scraper",
                  "currency_converter", "FINISH"]
    reasoning: str
    task: str


def supervisor(state: State):
    decision: SupervisorDecision = llm.with_structured_output(SupervisorDecision).invoke([
        SystemMessage(
            f"""
            You are a supervisor tasked with coordinating a multi-agent system.
            Your team includes the following workers:

            - **data_analyst**: Analyzes data and presents it in a clear, easy-to-digest format.
            - **scraper**: Uses a web scraper to search for product information on grocery store websites.
            - **currency_converter**: Converts values between currencies, such as USD to COP.

            Important for the supervisor:
            - Your role is to delegate tasks to the appropriate worker based on the user's request
            and the current stage of the task.
            - Assign one worker at a time.
            - Once the user request is fulfilled respond with `{FINISH_COMMAND}`.

            Output:
            - Justify your reasoning.
            - Explain the task to the worker as if you were the user, be very detailed, direct, and include what you expect from the worker.

            <task_progress>
            {[f"{message.type}{f' ({message.name})' if message.name else ''}: {message.content}" for message in state["messages"]]}
            </task_progress>
            """
        ),
    ])

    if (decision['next'] == FINISH_COMMAND):
        decision['next'] = END

    return {
        "next": decision['next'],
        "task": decision['task']
    }


def router(state: State):
    return state["next"]


def data_analyst(state: State):
    result = DataAnalystAgent.invoke({
        "data": state["messages"],
        "task": state['task']
    })

    return {
        "messages": [AIMessage(content=result["analysis"], name="data_analyst")],
        "next": "supervisor"
    }


def currency_converter(state: State):
    result = CurrencyConverterAgent.invoke({
        "messages": state["messages"] + [HumanMessage(content=state['task'])]
    })

    last_message = result["messages"][-1]

    return {
        "messages": [
            AIMessage(content=last_message.content,
                      name="currency_converter")
        ],
        "next": "supervisor"
    }


def scraper_agent(state: State):
    result = ScraperAgent.invoke({
        "messages": state["messages"] + [HumanMessage(content=state['task'])]
    })

    return {
        "messages": [AIMessage(content=json.dumps(result["extracted_products"]), name="scraper_agent")],
        "next": "supervisor"
    }


graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("supervisor", supervisor)
graph_builder.add_node("data_analyst", data_analyst)
graph_builder.add_node("currency_converter", currency_converter)
graph_builder.add_node("scraper", scraper_agent)

# Edges
graph_builder.add_edge(START, "supervisor")
graph_builder.add_conditional_edges("supervisor", router, workers + [END])
graph_builder.add_edge("data_analyst", "supervisor")
graph_builder.add_edge("currency_converter", "supervisor")
graph_builder.add_edge("scraper", "supervisor")


agent = graph_builder.compile()
