import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq

# Load GROQ_API_KEY from the .env file
load_dotenv()

# Page settings
st.set_page_config(
    page_title="Chatbot",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Generative AI Chatbot")

# Create chat memory (only the first time)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show all previous messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Connect to the AI model
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.0
)


# Input box at the bottom
user_prompt = st.chat_input("Ask Chatbot...")

if user_prompt:
    # Show and save the user's message
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Send the conversation to the AI
    response = llm.invoke(
        input=[{"role": "system", "content": "You are a helpful assistant"},
               *st.session_state.chat_history]
    )
    assistant_response = response.content

    # Save and show the AI's reply
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

    with st.chat_message("assistant"):
        st.markdown(assistant_response)