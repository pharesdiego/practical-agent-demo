from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from typing import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


class State(TypedDict):
    data: str
    task: str
    plan: str
    analysis: str


llm = ChatOpenAI(
    openai_api_key=getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="google/gemini-2.0-flash-001",
    temperature=0.4
)


def planner(state: State):
    generated_plan = llm.invoke([
        SystemMessage(
            """
            You are a planner agent. Your role is to analyze and describe data to build context,
            then create structured plans using markdown lists. Start by explaining the data clearly
            and concisely. Identify key variables, patterns, or anomalies. Then, outline a logical plan
            or set of next steps using bullet points or numbered lists in markdown format.
            Keep your tone focused, organized, and easy to follow.

            Do not perform the task your self, just generate a plan for an expert data analyst to follow.
            """
        ),
        HumanMessage(
            f"""
            <task>{state['task']}</task>
            <data>{state['data']}</data>
            """)
    ])

    return {
        "plan": generated_plan.content,
    }


def data_analyst(state: State):
    result = llm \
        .invoke([SystemMessage(
            f"""
            You are an expert data analyst. You can analyze structured and unstructured data,
            clean and transform it into various formats (e.g., CSV, JSON, SQL),
            and extract clear, actionable insights. When needed, provide visualizations,
            summaries, and explain your reasoning in a concise and professional tone.

            Requirements:
            - Analyze the plan and follow it.

            <plan>
            {state["plan"]}
            </plan>

            <data>
            {state["data"]}
            </data>
            """
        )])

    return {
        "analysis": result.content,
    }


graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("planner", planner)
graph_builder.add_node("data_analyst", data_analyst)

# Edges
graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "data_analyst")
graph_builder.add_edge("data_analyst", END)

agent = graph_builder.compile()
