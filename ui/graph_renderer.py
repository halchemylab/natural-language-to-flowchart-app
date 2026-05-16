import graphviz

from graph_schema import Graph

EXPORT_FORMATS = {"svg", "png", "pdf"}


def _coerce_graph(graph_data) -> Graph:
    if isinstance(graph_data, Graph):
        return graph_data
    return Graph.model_validate(graph_data)


def create_graphviz_chart(graph_data, node_shape, node_color, font, layout_algorithm):
    graph = _coerce_graph(graph_data)
    dot = graphviz.Digraph()
    rankdir = graph.layout.direction

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

    for node in graph.nodes:
        color = node_colors.get(node.group, node_color)
        dot.node(node.id, node.label, fillcolor=color)

    for edge in graph.edges:
        dot.edge(edge.source, edge.target, edge.label)
    return dot

def render_graph_export(graph_data, node_shape, node_color, font, layout_algorithm, output_format):
    if output_format not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {output_format}")

    chart = create_graphviz_chart(graph_data, node_shape, node_color, font, layout_algorithm)
    return chart.pipe(format=output_format)
