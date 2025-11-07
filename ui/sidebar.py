import streamlit as st
import json
from graph_schema import Graph
from config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    MODEL_OPTIONS,
    NODE_SHAPE_OPTIONS,
    DEFAULT_NODE_SHAPE,
    DEFAULT_NODE_COLOR,
    FONT_OPTIONS,
    DEFAULT_FONT,
    LAYOUT_ALGORITHM_OPTIONS,
    DEFAULT_LAYOUT_ALGORITHM,
)
from .metrics import load_metrics

def display_metrics():
    # Custom CSS to style the metric containers
    st.markdown("""
    <style>
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    metrics = load_metrics()
    run_count = metrics.get("run_count", 0)
    time_saved = run_count * 30
    money_saved = run_count * 25

    st.header("📊 ROI Metrics")
    st.metric(label="Usage", value=f"{run_count} times")
    st.metric(label="Time Saved", value=f"{time_saved} mins")
    st.metric(label="Money Saved", value=f"${money_saved}")

def render_sidebar():
    with st.sidebar:
        display_metrics()
        st.header("⚙️ Configuration")

        st.session_state.api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your key from https://platform.openai.com/account/api-keys",
        )

        model = st.selectbox("Model", MODEL_OPTIONS, index=MODEL_OPTIONS.index(DEFAULT_MODEL))

        temperature = st.slider(
            "Temperature", 0.0, 1.0, float(st.session_state.get("TEMPERATURE", DEFAULT_TEMPERATURE)), 0.05,
            help="Lower values make the output more deterministic."
        )

        st.markdown("---")
        st.header("🎨 Styling Options")
        st.session_state.node_shape = st.selectbox("Node Shape", NODE_SHAPE_OPTIONS, index=NODE_SHAPE_OPTIONS.index(DEFAULT_NODE_SHAPE))
        st.session_state.node_color = st.color_picker("Node Color", DEFAULT_NODE_COLOR)
        st.session_state.font = st.selectbox("Font", FONT_OPTIONS, index=FONT_OPTIONS.index(DEFAULT_FONT))
        st.session_state.layout_algorithm = st.selectbox("Layout Algorithm", LAYOUT_ALGORITHM_OPTIONS, index=LAYOUT_ALGORITHM_OPTIONS.index(DEFAULT_LAYOUT_ALGORITHM))

        st.markdown("---")
        st.header("📥 Import")
        uploaded_graph = st.file_uploader("Load GRAPH JSON", type=["json"])
        if uploaded_graph:
            try:
                graph_json = json.load(uploaded_graph)
                st.session_state.graph_data = Graph.model_validate(graph_json).model_dump()
                st.toast("✅ Graph JSON loaded successfully!", icon="🎉")
            except (json.JSONDecodeError, Exception) as e:
                st.error(f"Invalid JSON file: {e}")

        uploaded_layout = st.file_uploader("Load Layout JSON", type=["json"])
        if uploaded_layout:
            try:
                st.session_state.graph_layout = json.load(uploaded_layout)
                st.toast("✅ Layout loaded successfully!", icon="🗺️")
            except json.JSONDecodeError:
                st.error("Invalid layout JSON file.")


        st.markdown("---")
        st.header("📤 Export")

        if st.session_state.graph_data:
            st.download_button(
                label="Save GRAPH JSON",
                data=json.dumps(st.session_state.graph_data, indent=2),
                file_name="graph.json",
                mime="application/json",
            )
            if st.session_state.graph_layout:
                st.download_button(
                    label="Save Layout JSON",
                    data=json.dumps(st.session_state.graph_layout, indent=2),
                    file_name="layout.json",
                    mime="application/json",
                )

            st.markdown('<div id="export-buttons"></div>', unsafe_allow_html=True)
            st.markdown(
                """
                <small>PNG/SVG exports are generated client-side. PDF is generated on the server.</small>
                """,
                unsafe_allow_html=True
            )
    return model, temperature
