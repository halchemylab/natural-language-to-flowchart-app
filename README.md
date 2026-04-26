# Natural Language to Flowchart App

This Streamlit application transforms natural-language descriptions of processes into flowcharts. It uses an AI model to generate a validated graph structure, then renders the result with Graphviz inside Streamlit.

## Features

-   **AI-Powered Graph Generation**: Describe a process in plain English, and the app generates a flowchart diagram.
-   **Graphviz Rendering**: Render validated graphs as clean directed flowcharts.
-   **Import & Export**: Load graph JSON and export the graph as JSON, SVG, PNG, or PDF.
-   **Configurable**: Adjust the AI model, temperature, layout algorithm, node shape, color, and font.
-   **Repair Retries**: Retry malformed model responses with a repair prompt before surfacing an error.

## Tech Stack

-   **Backend**: Python 3.11+, Streamlit, OpenAI API
-   **Rendering**: Graphviz for flowchart rendering.
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
4.  **Customize Rendering**:
    -   Use the sidebar to adjust node shape, color, font, and the Graphviz layout algorithm.
5.  **Save & Export**:
    -   Use the sidebar buttons to export the diagram as a PNG, SVG, or PDF.
    -   Save the generated `graph.json` for later use.

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
├── static/                   # Bundled static assets from earlier UI experiments
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
