"""
Centralized configuration for the Natural Language to Flowchart application.
"""

# --- LLM Configuration ---
DEFAULT_MODEL = "gpt-4-turbo"
DEFAULT_TEMPERATURE = 0.2
MAX_RETRIES = 2
MODEL_OPTIONS = ["gpt-5-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

# --- UI Configuration ---
DEFAULT_NODE_SHAPE = "box"
DEFAULT_NODE_COLOR = "#f0f0f0"
DEFAULT_FONT = "Arial"
DEFAULT_LAYOUT_ALGORITHM = "dot"

NODE_SHAPE_OPTIONS = ["box", "ellipse", "diamond", "circle"]
FONT_OPTIONS = ["Arial", "Helvetica", "Times New Roman"]
LAYOUT_ALGORITHM_OPTIONS = ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]

# --- Default Prompt ---
DEFAULT_PROMPT = """
Process: User Authentication Flow
1. User visits the website and sees a login page.
2. User enters their email and password.
3. The system checks if the credentials are valid.
4. If they are valid, the user is redirected to their dashboard.
5. If they are invalid, an error message "Invalid credentials" is shown.
6. From the dashboard, the user can log out.
"""
