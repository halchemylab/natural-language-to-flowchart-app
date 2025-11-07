import streamlit as st
import logging
import time
from llm_client import generate_graph_from_text, GraphGenerationError
from .metrics import load_metrics, save_metrics
from .graph_renderer import create_graphviz_chart

def render_main_panel(model, temperature):
    st.title("✨ Natural Language to Flowchart")
    st.caption("Describe a process, and watch it turn into an editable flowchart. Powered by AI.")

    col1, col2 = st.columns(2)

    with col1:
        user_prompt = st.text_area(
            "Enter your process description:",
            value=st.session_state.DEFAULT_PROMPT,
            height=300,
            key="user_prompt_input"
        )

        status_placeholder = st.empty()

        if st.button("🚀 Generate Draft", type="primary", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Please enter your OpenAI API key in the sidebar.")
            elif not user_prompt.strip():
                st.warning("Please enter a description.")
            else:
                try:
                    with st.spinner("✨ Kicking off the magic..."):
                        status_placeholder.info("✨ Kicking off the magic...", icon="⏳")
                        
                        def status_callback(message):
                            status_placeholder.info(message, icon="⏳")

                        start_time = time.time()
                        graph = generate_graph_from_text(
                            api_key=st.session_state.api_key,
                            text=user_prompt,
                            model=model,
                            temperature=temperature,
                            status_callback=status_callback,
                        )
                        st.session_state.graph_data = graph.model_dump()
                        st.session_state.last_generated_text = user_prompt
                        st.session_state.generation_error = None
                        st.session_state.graph_layout = {} # Reset layout on new generation

                        metrics = load_metrics()
                        metrics["run_count"] = metrics.get("run_count", 0) + 1
                        save_metrics(metrics)
                        
                        end_time = time.time()
                        status_placeholder.success(f"✅ Graph generated in {end_time - start_time:.2f}s!", icon="🎉")
                        st.rerun()

                except GraphGenerationError as e:
                    st.session_state.graph_data = None
                    st.session_state.generation_error = str(e)
                    status_placeholder.empty()
                    if "401" in str(e):
                        st.error("Invalid OpenAI API key. Please check your key in the sidebar.", icon="🔥")
                    else:
                        st.error(f"Failed to generate graph: {e}", icon="🔥")
                except Exception as e:
                    st.session_state.graph_data = None
                    st.session_state.generation_error = f"An unexpected error occurred: {e}"
                    status_placeholder.empty()
                    st.error(f"An unexpected error occurred: {e}", icon="🔥")
    
    with col2:
        if st.session_state.graph_data:
            logging.info(f"Rendering graph with data: {st.session_state.graph_data}")
            status_placeholder.info("🎨 Rendering graph...", icon="🖌️")
            # Create a graphviz chart
            dot = create_graphviz_chart(
                st.session_state.graph_data,
                st.session_state.node_shape,
                st.session_state.node_color,
                st.session_state.font,
                st.session_state.layout_algorithm
            )
            st.graphviz_chart(dot)
            status_placeholder.empty()

        elif st.session_state.generation_error:
            st.error(f"**Error during generation:**\n\n{st.session_state.generation_error}", icon="🚨")
            if st.button("Retry"):
                st.rerun()
        elif not st.session_state.graph_data:
            st.warning("Graph data is not available. Please generate a graph first.")
        else:
            st.info("Enter a description above and click 'Generate Draft' to create a flowchart.")
