import streamlit as st
import json
from graph_schema import Graph
import logging
import graphviz
import time
from llm_client import generate_graph_from_text, GraphGenerationError

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.session_state.api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your key from https://platform.openai.com/account/api-keys",
        )

        model_options = ["gpt-5-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        model = st.selectbox("Model", model_options, index=1) # Default to gpt-4-turbo

        temperature = st.slider(
            "Temperature", 0.0, 1.0, float(st.session_state.get("TEMPERATURE", 0.2)), 0.05,
            help="Lower values make the output more deterministic."
        )

        layout_direction = st.selectbox("Layout Direction", ["TB", "LR"], index=0, help="Top-to-Bottom or Left-to-Right.")

        st.session_state.theme = st.selectbox("Theme", ["light", "dark"], index=0)
        st.session_state.show_physics = st.toggle("Enable Physics", value=True, help="Enable/disable the physics simulation for layout.")

        st.markdown("---")
        st.header("🎨 Styling Options")
        st.session_state.node_shape = st.selectbox("Node Shape", ["box", "ellipse", "diamond", "circle"], index=0)
        st.session_state.node_color = st.color_picker("Node Color", "#f0f0f0")
        st.session_state.font = st.selectbox("Font", ["Arial", "Helvetica", "Times New Roman"], index=0)
        st.session_state.layout_algorithm = st.selectbox("Layout Algorithm", ["dot", "neato", "fdp", "sfdp", "twopi", "circo"], index=0)

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
    return model, temperature, layout_direction

def render_main_panel(DEFAULT_PROMPT, model, temperature):
    st.title("✨ Natural Language to Flowchart")
    st.caption("Describe a process, and watch it turn into an editable flowchart. Powered by AI.")

    col1, col2 = st.columns(2)

    with col1:
        user_prompt = st.text_area(
            "Enter your process description:",
            value=DEFAULT_PROMPT,
            height=300,
            key="user_prompt_input"
        )

        if st.button("🚀 Generate Draft", type="primary", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Please enter your OpenAI API key in the sidebar.")
            elif not user_prompt.strip():
                st.warning("Please enter a description.")
            else:
                with st.spinner("✨ Generating graph from your text..."):
                    try:
                        start_time = time.time()
                        graph = generate_graph_from_text(
                            api_key=st.session_state.api_key,
                            text=user_prompt,
                            model=model,
                            temperature=temperature,
                        )
                        st.session_state.graph_data = graph.model_dump()
                        st.session_state.last_generated_text = user_prompt
                        st.session_state.generation_error = None
                        st.session_state.graph_.layout = {} # Reset layout on new generation
                        end_time = time.time()
                        st.toast(f"✅ Graph generated in {end_time - start_time:.2f}s!", icon="🎉")
                    except GraphGenerationError as e:
                        st.session_state.graph_data = None
                        st.session_state.generation_error = str(e)
                        if "401" in str(e):
                            st.error("Invalid OpenAI API key. Please check your key in the sidebar.", icon="🔥")
                        else:
                            st.error(f"Failed to generate graph: {e}", icon="🔥")
                    except Exception as e:
                        st.session_state.graph_data = None
                        st.session_state.generation_error = f"An unexpected error occurred: {e}"
                        st.error(f"An unexpected error occurred: {e}", icon="🔥")
    
    with col2:
        if st.session_state.graph_data:
            logging.info(f"Rendering graph with data: {st.session_state.graph_data}")
            # Create a graphviz chart
            dot = create_graphviz_chart(
                st.session_state.graph_data,
                st.session_state.node_shape,
                st.session_state.node_color,
                st.session_state.font,
                st.session_state.layout_algorithm
            )
            st.graphviz_chart(dot)

        elif st.session_state.generation_error:
            st.error(f"**Error during generation:**\n\n{st.session_state.generation_error}", icon="🚨")
            if st.button("Retry"):
                st.rerun()
        elif not st.session_state.graph_data:
            st.warning("Graph data is not available. Please generate a graph first.")
        else:
            st.info("Enter a description above and click 'Generate Draft' to create a flowchart.")

def create_graphviz_chart(graph_data, node_shape, node_color, font, layout_algorithm):
    dot = graphviz.Digraph()
    dot.attr('graph', layout=layout_algorithm, rankdir='TB', splines='ortho', nodesep='0.8', ranksep='0.8')
    dot.attr('node', shape=node_shape, style='rounded,filled', fillcolor=node_color, fontname=font, fontsize='12')
    dot.attr('edge', color='#808080', fontname=font, fontsize='10')

    node_colors = {
        "process": "#e6f7ff",
        "decision": "#fffbe6",
        "interface": "#f6ffed",
        "user": "#e6e6ff",
        "system": "#f0f0f0",
    }

    if "nodes" in graph_data:
        for node in graph_data["nodes"]:
            group = node.get("group", "default")
            color = node_colors.get(group, node_color)
            dot.node(node["id"], node["label"], fillcolor=color)
    if "edges" in graph_data:
        for edge in graph_data["edges"]:
            dot.edge(edge["source"], edge["target"], edge.get("label"))
    return dot