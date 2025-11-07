import streamlit as st
from dotenv import load_dotenv
import os
from ui import render_sidebar, render_main_panel
from config import DEFAULT_PROMPT

# --- Page Configuration ---
st.set_page_config(
    page_title="Natural Language to Flowchart",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Environment Variables ---
load_dotenv()

# --- Session State Initialization ---
def init_session_state():
    """Initialize session state variables if they don't exist."""
    defaults = {
        "graph_data": None,
        "graph_layout": {},
        "last_generated_text": "",
        "generation_error": None,
        "api_key": os.getenv("OPENAI_API_KEY") or "",
        "DEFAULT_PROMPT": DEFAULT_PROMPT
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- Render UI ---
model, temperature = render_sidebar()
render_main_panel(model, temperature)
# --- Footer ---
st.markdown("---")
st.markdown(
    "Made with 🧠 by a human and an AI assistant. "
)