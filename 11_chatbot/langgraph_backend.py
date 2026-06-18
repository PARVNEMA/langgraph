from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
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

checkpointer = InMemorySaver()
workflow = graph.compile(checkpointer=checkpointer)

# ? Streaming in langgraph is a concept in which we are genreating content one by one instead of generating whole at once it is useful for making our ai behavior just like human , intruppt ai and save tokens

# ? we will use workflow.stream function which will return us an generator(iterator) which uses yield to provide content on the flow

# for message_chunk,meta_data in workflow.stream({"messages": [HumanMessage(content="tell me how to avoid comparision ?")]},config={"configurable": {"thread_id": "1"}},
# stream_mode="messages"):
#     print(message_chunk.text,end=" ",flush=True)