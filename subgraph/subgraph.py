from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class substate(TypedDict):
  input_text:str
  translated_text:str


subgraph_llm=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, max_tokens=1000)


def translate_text(state:substate):
  prompt=f"Translate the following text to hindi:\n {state['input_text']}"
  translated_text=subgraph_llm.invoke(prompt).content

  return {"translated_text":translated_text}


subgraph_builder=StateGraph(substate)

subgraph_builder.add_node('translate_node',translate_text)

subgraph_builder.add_edge(START,'translate_node')
subgraph_builder.add_edge('translate_node',END)

subgraph=subgraph_builder.compile()


class parentstate(TypedDict):
  question:str
  answer_eng:str
  answer_hind:str

parent_llm=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, max_tokens=1000)

def generate_answer(state:parentstate):
  answer=parent_llm.invoke(state['question']).content
  return {"answer_eng":answer}

def translate_answer(state:parentstate):
  prompt=f"Translate the following text to hindi:\n {state['answer_eng']}"
  translated_text=subgraph_llm.invoke(prompt).content

  return {"answer_hind":translated_text}


parent_Builder=StateGraph(parentstate)

parent_Builder.add_node('generate_node',generate_answer)
parent_Builder.add_node('translate_node',translate_answer)

parent_Builder.add_edge(START,'generate_node')
parent_Builder.add_edge('generate_node','translate_node')
parent_Builder.add_edge('translate_node',END)

graph=parent_Builder.compile()

graph.invoke({'question': 'What is quantum physics'})