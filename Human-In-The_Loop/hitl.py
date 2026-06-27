from langgraph.types import interrupt,Command
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langgraph.graph.message import add_messages

load_dotenv()
llm=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, max_tokens=1000)

class chat_state(TypedDict):
  messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state:chat_state):
  decision=interrupt({
    "type":"approval",
    "reason":"Do you want to continue?",
    "question":state["messages"][-1].content,
    "instructions":"Respond with 'yes' or 'no'."
      })

  approved = str(decision.get("approved", "")).strip().lower()

  if approved == 'no':
      return {"messages": [AIMessage(content="Goodbye!")]}
  else :
    response =llm.invoke(state["messages"])

    return {"messages": [response]}


graph=StateGraph(chat_state)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

checkpointer=InMemorySaver()

app=graph.compile(checkpointer=checkpointer)

config={
  "configurable":{
    "thread_id":"1"
}}

initial_input={
  "messages":[
    HumanMessage(content="my name is naman?")
  ]
}

result=app.invoke(initial_input,config=config)

message=result["__interrupt__"][0].value


user_input=input(f"user: {message} approve or reject")

# ? have to invoke the graph as many number of time as we have asked user for input
final_result=app.invoke(Command(resume={"approved": user_input.strip().lower()}),config=config )

print(final_result)

