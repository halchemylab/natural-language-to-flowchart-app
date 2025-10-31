# Natural Language to Flowchart App

This Streamlit application transforms natural-language descriptions of processes into beautiful, editable flowcharts. It uses an AI model (OpenAI's GPT series) to generate a graph structure, which is then rendered in an interactive drag-and-drop editor.

## Features

-   **AI-Powered Graph Generation**: Describe a process in plain English, and the app generates a flowchart diagram.
-   **Interactive Editor**: Freely drag, pan, and zoom the diagram to get the perfect layout.
-   **Editable Nodes & Edges**: (Future goal) Click to edit labels, shapes, and connections.
-   **Multiple Export Options**: Export your finished diagram to PNG, SVG, or PDF.
-   **Layout Persistence**: Save your custom node positions and reload them later.
-   **Offline First**: Renders graphs even without an internet connection (after initial setup). All libraries are bundled.
-   **Configurable**: Adjust the AI model, temperature, layout direction, and theme.

## Tech Stack

-   **Backend**: Python 3.11+, Streamlit, OpenAI API
-   **Frontend**: `vis-network` for graph rendering, `dom-to-image-more` for client-side exports.
-   **Validation**: Pydantic for robust JSON schema validation.
-   **Export**: CairoSVG for server-side SVG to PDF conversion.

## Getting Started

### Prerequisites

-   Python 3.11 or newer
-   An OpenAI API Key

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/natural-language-to-flowchart-app.git
    cd natural-language-to-flowchart-app
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    -   Copy the example `.env` file:
        ```bash
        cp .env.example .env
        ```
    -   Open the `.env` file and add your OpenAI API key:
        ```
        OPENAI_API_KEY="sk-..."
        ```

### Running the Application

Launch the Streamlit app with the provided shell script:

```bash
# On Linux/macOS
chmod +x scripts/dev_run.sh
./scripts/dev_run.sh

# On Windows
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`.

## How to Use

1.  **Enter Your API Key**: If you haven't set it in your `.env` file, you can enter your OpenAI API key in the sidebar.
2.  **Write a Description**: In the main text area, describe the process you want to visualize. An example is pre-filled for you.
3.  **Generate Draft**: Click the "Generate draft" button. The app will call the OpenAI API, validate the response, and render the initial flowchart.
4.  **Customize Layout**:
    -   Drag nodes to rearrange them.
    -   Use the toolbar to fit the diagram to the screen, or lock/unlock the physics simulation.
    -   Pan and zoom using your mouse/trackpad.
5.  **Save & Export**:
    -   Use the sidebar buttons to export the diagram as a PNG, SVG, or PDF.
    -   Save the generated `graph.json` (the raw nodes and edges) or the `layout.json` (your custom node positions) for later use.

## Project Structure

```
.
├── app.py                    # Main Streamlit application
├── llm_client.py             # OpenAI API client and validation logic
├── graph_schema.py           # Pydantic models for graph JSON validation
├── prompts.py                # Prompts for the LLM
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md                 # This file
├── components/
│   └── graph.html            # HTML/JS for the interactive graph component
├── static/
│   ├── dom-to-image-more.min.js # JS library for client-side export
│   └── vis-network.min.js    # JS library for graph rendering
├── utils/
│   └── export.py             # Server-side export utilities (e.g., SVG to PDF)
├── sample_data/
│   └── sample.json           # An example graph JSON file
├── tests/
│   └── test_schema.py        # Unit tests for the graph schema
└── scripts/
    ├── dev_run.sh            # Development run script
    └── export_cli.py         # CLI tool for batch exports
```

## Smoke Test

To verify that the core components are working:

1.  Run the test suite for the schema validation:
    ```bash
    pytest tests/test_schema.py
    ```
    This ensures that the data validation logic is correct.

2.  Use the command-line export script:
    ```bash
    python scripts/export_cli.py sample_data/sample.json output/sample.svg
    python scripts/export_cli.py sample_data/sample.json output/sample.pdf
    ```
    This tests the server-side export functionality independently of the Streamlit app.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.