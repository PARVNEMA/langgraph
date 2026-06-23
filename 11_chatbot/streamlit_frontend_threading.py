import streamlit as st
from langgraph_backend import workflow
from langchain_core.messages import HumanMessage
import uuid


# ********************** utility functions **********************
def generate_thread_id():
  return uuid.uuid4()

def reset_chat():

    st.session_state['memory_input']=[]
    add_threads(st.session_state['thread_id'])
    st.session_state['thread_id'] = generate_thread_id()

def add_threads(thread_id):
  if thread_id not in st.session_state['chat_thread']:
    st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
  state= workflow.get_state(config={"configurable": {"thread_id": thread_id}})
  return state.values.get('messages',[])

# ? initialize the session state sessions
# * st.session_state -> stores the state of the session and doesn't refresh
if "memory_input" not in st.session_state:
    st.session_state["memory_input"] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread']=[]

add_threads(st.session_state['thread_id'])
# ************************ SideBar ************************

st.sidebar.title("Langgraph Chatbot")

if st.sidebar.button("New Chat"):
  reset_chat()

st.sidebar.title("Chat History")

for thread_id in st.session_state['chat_thread']:
  messages=load_conversation(thread_id)
  text_message=thread_id
  if len(messages) >0 :
    text_message = messages[0].text
  else:
    text_message = thread_id
  if st.sidebar.button(str(text_message),key=thread_id):
    st.session_state['thread_id'] = thread_id
    temp_messages=[]

    for message in messages:
      if isinstance(message,HumanMessage):
        role='user'
      else:
        role='assistant'
      temp_messages.append({"role":role,"content":message.text})

    st.session_state['memory_input'] = temp_messages


# ******************** session setup **************************
# * load conversation history
for message in st.session_state["memory_input"]:
    st.chat_message(message["role"]).write(message["content"])


config1 = {"configurable": {"thread_id": st.session_state['thread_id']}}

# * takes the user_input
user_input = st.chat_input("type here")

if user_input:
    # * saves user answers in the memory
    st.session_state["memory_input"].append({"role":"user","content":user_input})
    st.chat_message("user").write(user_input)

    # response = workflow.invoke({"messages": [HumanMessage(content=user_input)]}, config=config1)
    # ai_response = response["messages"][-1].content
    # st.session_state["memory_input"].append({"role":"assistant","content":ai_response})
    # st.chat_message("assistant").write(ai_response)
    with st.chat_message("assistant"):
        # * accepts the generator object and prints it with typewriter effect
        ai_message= st.write_stream(message_chunk.text for message_chunk,metadata in workflow.stream({"messages": [HumanMessage(content=user_input)]},config=config1,stream_mode="messages"))
        st.session_state["memory_input"].append({"role":"assistant","content":ai_message})



