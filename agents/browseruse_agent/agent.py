from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from browser_use import Agent as BrowserUseAgent, Browser, BrowserConfig, Controller
from pydantic import BaseModel

load_dotenv()


class Product(BaseModel):
    name: str
    price: str


class Products(BaseModel):
    products: List[Product]


class State(TypedDict):
    messages: str
    extracted_products: str


browser = Browser(
    config=BrowserConfig(
        # Specify the path to your Chrome executable
        chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
    )
)

controller = Controller(output_model=Products)

llm = ChatOpenAI(
    openai_api_key=getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openai/gpt-4o-2024-11-20",
    temperature=0
)


async def worker(state: State):
    messages: Sequence[BaseMessage] = [
        f'{message.type}: {message.content}' for message in state["messages"]]

    agent = BrowserUseAgent(
        llm=llm,
        task=f"""You are an intelligent agent capable of generating search queries
            to be used in a groceries store search input.

            The search input expects well formatted product/ingredient/fruit names in singular,
            for example: "carrot", "pepper", "bread".

            Task: Analyze the conversation between the assistant and the user to figure what search queries
            are the best so that the inferred user's requirement is fulfilled.

            Restrictions:
            - You must only visit http://localhost:7070/. Do not use any other website.

            <conversation>
            {'\n'.join(messages)}
            </conversation>""",
        browser=browser,
        controller=controller,
        generate_gif=False,
        validate_output=True
    )
    history = await agent.run()
    result = history.final_result()

    if result:
        parsed: Products = Products.model_validate_json(result)

        return {
            "extracted_products": [product.model_dump_json() for product in parsed.products]
        }

    return {
        "extracted_products": []
    }


graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("worker", worker)

# Edges
graph_builder.add_edge(START, "worker")
graph_builder.add_edge("worker", END)

agent = graph_builder.compile()
