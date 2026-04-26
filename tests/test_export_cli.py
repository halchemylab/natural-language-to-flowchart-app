from graph_schema import Graph
from scripts.export_cli import render_graph_to_svg


def test_render_graph_to_svg_escapes_node_labels():
    graph = Graph.model_validate({
        "nodes": [{"id": "A", "label": "Start <now> & \"go\""}],
        "edges": [],
    })

    svg = render_graph_to_svg(graph)

    assert "Start &lt;now&gt; &amp; &quot;go&quot;" in svg
    assert "Start <now>" not in svg
