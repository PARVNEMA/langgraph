import streamlit as st
from langgraph_backend import workflow
from langchain_core.messages import HumanMessage

config1 = {"configurable": {"thread_id": "1"}}

# st.session_state -> stores the state of the session and doesn't refresh
if "memory_input" not in st.session_state:
    st.session_state["memory_input"] = []

# * load conversation history
for message in st.session_state["memory_input"]:
    st.chat_message(message["role"]).write(message["content"])

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



