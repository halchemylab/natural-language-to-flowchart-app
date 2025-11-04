import streamlit as st
from dotenv import load_dotenv
import os
from ui import render_sidebar, render_main_panel

# --- Page Configuration ---
st.set_page_config(
    page_title="Natural Language to Flowchart",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Environment Variables ---
load_dotenv()

# --- Constants ---
DEFAULT_PROMPT = """
Process: User Authentication Flow
1. User visits the website and sees a login page.
2. User enters their email and password.
3. The system checks if the credentials are valid.
4. If they are valid, the user is redirected to their dashboard.
5. If they are invalid, an error message "Invalid credentials" is shown.
6. From the dashboard, the user can log out.
"""

# --- Session State Initialization ---
def init_session_state():
    """Initialize session state variables if they don't exist."""
    defaults = {
        "graph_data": None,
        "graph_layout": {},
        "last_generated_text": "",
        "theme": "light",
        "show_physics": True,
        "generation_error": None,
        "api_key": os.getenv("OPENAI_API_KEY") or "",
        "DEFAULT_PROMPT": DEFAULT_PROMPT
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- Render UI ---
model, temperature, layout_direction = render_sidebar()
render_main_panel(DEFAULT_PROMPT, model, temperature)

# --- Footer ---
st.markdown("---")
st.markdown(
    "Made with ❤️ by an AI assistant. "
)