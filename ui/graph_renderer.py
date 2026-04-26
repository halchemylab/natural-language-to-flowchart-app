import graphviz

EXPORT_FORMATS = {"svg", "png", "pdf"}

def create_graphviz_chart(graph_data, node_shape, node_color, font, layout_algorithm):
    dot = graphviz.Digraph()
    layout = graph_data.get("layout", {})
    rankdir = layout.get("direction", "TB")
    if rankdir not in {"TB", "LR"}:
        rankdir = "TB"

    dot.attr('graph', layout=layout_algorithm, rankdir=rankdir, splines='ortho', nodesep='0.8', ranksep='0.8')
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

def render_graph_export(graph_data, node_shape, node_color, font, layout_algorithm, output_format):
    if output_format not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {output_format}")

    chart = create_graphviz_chart(graph_data, node_shape, node_color, font, layout_algorithm)
    return chart.pipe(format=output_format)
