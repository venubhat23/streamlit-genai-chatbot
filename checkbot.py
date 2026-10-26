import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq

# Load GROQ_API_KEY from the .env file
load_dotenv()

# Page settings
st.set_page_config(
    page_title="Nova · AI Chatbot",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, .stChatInput textarea {
        font-family: 'Inter', sans-serif !important;
    }

    /* Animated gradient background */
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(139, 92, 246, 0.18), transparent 40%),
            radial-gradient(circle at 85% 20%, rgba(236, 72, 153, 0.14), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(59, 130, 246, 0.12), transparent 50%),
            #0B0F1A;
        background-attachment: fixed;
    }

    #MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }
    .block-container { padding-top: 2.5rem; padding-bottom: 6rem; max-width: 820px; }

    /* Hero header */
    .hero { text-align: center; margin-bottom: 1.8rem; animation: fadeIn .6s ease-out; }
    .hero-badge {
        display: inline-block; padding: 4px 14px; border-radius: 999px;
        background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.35);
        color: #C4B5FD; font-size: 0.78rem; font-weight: 600; letter-spacing: .04em;
        margin-bottom: 0.9rem;
    }
    .hero h1 {
        font-size: 3rem; font-weight: 800; margin: 0; line-height: 1.1;
        background: linear-gradient(90deg, #A78BFA, #EC4899, #60A5FA, #A78BFA);
        background-size: 300% auto;
        -webkit-background-clip: text; background-clip: text; color: transparent;
        animation: shine 8s linear infinite;
    }
    .hero p { color: #9AA3B8; font-size: 1.05rem; margin-top: 0.6rem; }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(20, 26, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        animation: slideUp .35s ease-out;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.22), rgba(236, 72, 153, 0.14));
        border: 1px solid rgba(139, 92, 246, 0.35);
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.08), 0 10px 30px rgba(0, 0, 0, 0.35);
    }

    /* Suggestion buttons */
    .stButton > button {
        width: 100%; text-align: left; border-radius: 14px; padding: 0.85rem 1rem;
        background: rgba(20, 26, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08);
        color: #D6DAE6; font-weight: 500; transition: all .2s ease;
    }
    .stButton > button:hover {
        border-color: #8B5CF6; color: #fff; transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.25);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(14, 18, 30, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    .sidebar-brand {
        font-size: 1.4rem; font-weight: 800; margin-bottom: 0.2rem;
        background: linear-gradient(90deg, #A78BFA, #EC4899);
        -webkit-background-clip: text; background-clip: text; color: transparent;
    }
    .stat-card {
        background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 12px; padding: 0.7rem 0.9rem; margin-top: 0.5rem;
        color: #C4B5FD; font-size: 0.85rem;
    }

    @keyframes shine { to { background-position: 300% center; } }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }
    @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
    </style>
    """,
    unsafe_allow_html=True,
)

USER_AVATAR = "🧑‍💻"
BOT_AVATAR = "✨"

# Create chat memory (only the first time)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar settings
with st.sidebar:
    st.markdown('<div class="sidebar-brand">✨ Nova</div>', unsafe_allow_html=True)
    st.caption("Powered by Groq · lightning-fast inference")
    st.divider()

    temperature = st.slider("🌡️ Creativity", 0.0, 1.0, 0.0, 0.1,
                            help="Higher values give more creative, varied answers.")
    system_prompt = st.text_area("🧠 Personality", "You are a helpful assistant", height=90)

    st.markdown(
        f'<div class="stat-card">💬 {len(st.session_state.chat_history)} messages in this chat</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Hero header
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">⚡ GENERATIVE AI</div>
        <h1>How can I help you today?</h1>
        <p>Ask anything — code, ideas, explanations, or just a chat.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Connect to the AI model
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=temperature
)

# Starter prompts when the chat is empty
suggestion = None
if not st.session_state.chat_history:
    suggestions = [
        "💡 Explain quantum computing in simple terms",
        "🐍 Write a Python function to reverse a string",
        "✍️ Give me 5 creative startup ideas",
        "📚 Summarize the key ideas of machine learning",
    ]
    cols = st.columns(2)
    for i, text in enumerate(suggestions):
        if cols[i % 2].button(text, key=f"suggest_{i}"):
            suggestion = text.split(" ", 1)[1]

# Show all previous messages
for message in st.session_state.chat_history:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input box at the bottom
user_prompt = st.chat_input("Message Nova...") or suggestion

if user_prompt:
    # Show and save the user's message
    st.chat_message("user", avatar=USER_AVATAR).markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Send the conversation to the AI and stream the reply
    messages = [{"role": "system", "content": system_prompt}, *st.session_state.chat_history]
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        assistant_response = st.write_stream(chunk.content for chunk in llm.stream(messages))

    # Save the AI's reply
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
    st.rerun()
