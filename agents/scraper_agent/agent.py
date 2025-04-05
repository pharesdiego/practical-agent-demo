from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages
from agents.scraper_agent.utils.search_products import search_products, Product

load_dotenv()


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    queries: List[str]
    extracted_products: List[Product]


llm = ChatOpenAI(
    openai_api_key=getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openai/gpt-4o-2024-11-20",
    temperature=0.2
)


class QueryBuilderOutput(BaseModel):
    queries: List[str]
    user_requirement: str


def query_builder(state: State):
    messages: Sequence[BaseMessage] = [
        f'{message.type}: {message.content}' for message in state["messages"]]

    result: QueryBuilderOutput = llm \
        .with_structured_output(schema=QueryBuilderOutput) \
        .invoke([SystemMessage(
            f"""
            You are an intelligent agent capable of generating search queries
            to be used in a groceries store search input.

            The search input expects well formatted product/ingredient/fruit names in singular,
            for example: "carrot", "pepper", "bread".

            Task: Analyze the conversation between the assistant and the user to figure what search queries
            are the best so that the inferred user's requirement is fulfilled.

            <conversation>
            {'\n'.join(messages)}
            </conversation>
            """
        )])

    return {
        "queries": result.queries,
    }


def scraper(state: State):
    return {
        "extracted_products": [
            product.model_dump_json() for query in state["queries"] for product in search_products(query)
        ]
    }


graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("query_builder", query_builder)
graph_builder.add_node("scraper", scraper)

# Edges
graph_builder.add_edge(START, "query_builder")
graph_builder.add_edge("query_builder", "scraper")
graph_builder.add_edge("scraper", END)

agent = graph_builder.compile()
