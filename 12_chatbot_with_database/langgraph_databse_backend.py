from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
load_dotenv()

class ChatMessage(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, max_tokens=1000)

def chat_node(state:ChatMessage):
    messages = state["messages"]

    response = llm.invoke(messages)

    return {"messages": [response]}

graph = StateGraph(ChatMessage)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
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