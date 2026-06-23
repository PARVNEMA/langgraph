from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
import sqlite3
import requests
load_dotenv()


# ? Search Tools

search_tool=DuckDuckGoSearchRun()

@tool
def calculator(first_num:float,second_num:float,operation:str)->dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()

tools=[search_tool,calculator,get_stock_price]

class ChatMessage(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, max_tokens=1000)

llm_with_tools=llm.bind_tools(tools)
def chat_node(state:ChatMessage):
    messages = state["messages"]

    response = llm.invoke(messages)

    return {"messages": [response]}

tool_node=ToolNode(tools)

graph = StateGraph(ChatMessage)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")
graph.add_edge("chat_node", END)

conn=sqlite3.connect(database="langgraph.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
workflow = graph.compile(checkpointer=checkpointer)

# result=workflow.invoke({"messages": [HumanMessage(content="my name is naman?")]},config={"configurable": {"thread_id": "1"}})

# print(result)4
def retreive_threads_from_db():
    all_threads=set()
    for threads in checkpointer.list(None):
        all_threads.add(threads.config["configurable"]["thread_id"])
        return list(all_threads)

retreive_threads_from_db()