import pytest
from graphviz import Digraph
from pydantic import ValidationError

from graph_schema import Graph
from ui.graph_renderer import create_graphviz_chart, render_graph_export

@pytest.fixture
def sample_graph_data():
    return {
        "nodes": [
            {"id": "node1", "label": "Node 1", "group": "process"},
            {"id": "node2", "label": "Node 2", "group": "decision"},
            {"id": "node3", "label": "Node 3"}
        ],
        "edges": [
            {"source": "node1", "target": "node2", "label": "Edge 1"},
            {"source": "node2", "target": "node3"}
        ]
    }

def test_create_graphviz_chart_returns_digraph(sample_graph_data):
    # Act
    chart = create_graphviz_chart(sample_graph_data, "box", "#f0f0f0", "Arial", "dot")

    # Assert
    assert isinstance(chart, Digraph)

def test_create_graphviz_chart_nodes_and_edges(sample_graph_data):
    # Act
    chart = create_graphviz_chart(sample_graph_data, "box", "#f0f0f0", "Arial", "dot")
    chart_source = str(chart.source)

    # Assert
    # Check for node definitions
    assert 'node1 [label="Node 1" fillcolor="#e6f7ff"]' in chart_source
    assert 'node2 [label="Node 2" fillcolor="#fffbe6"]' in chart_source
    assert 'node3 [label="Node 3" fillcolor="#f0f0f0"]' in chart_source # Default color

    # Check for edge definitions
    assert 'node1 -> node2 [label="Edge 1"]' in chart_source
    assert 'node2 -> node3' in chart_source

def test_create_graphviz_chart_uses_graph_layout_direction(sample_graph_data):
    sample_graph_data["layout"] = {"direction": "LR"}

    chart = create_graphviz_chart(sample_graph_data, "box", "#f0f0f0", "Arial", "dot")

    assert "rankdir=LR" in chart.source

def test_create_graphviz_chart_accepts_graph_model(sample_graph_data):
    graph = Graph.model_validate(sample_graph_data)

    chart = create_graphviz_chart(graph, "box", "#f0f0f0", "Arial", "dot")

    assert isinstance(chart, Digraph)
    assert "node1" in chart.source


def test_create_graphviz_chart_rejects_invalid_layout_direction(sample_graph_data):
    sample_graph_data["layout"] = {"direction": "SIDEWAYS"}

    with pytest.raises(ValidationError):
        create_graphviz_chart(sample_graph_data, "box", "#f0f0f0", "Arial", "dot")

def test_create_graphviz_chart_rejects_edges_with_missing_nodes(sample_graph_data):
    sample_graph_data["edges"][0]["target"] = "missing"

    with pytest.raises(ValidationError, match="does not match any node ID"):
        create_graphviz_chart(sample_graph_data, "box", "#f0f0f0", "Arial", "dot")

def test_render_graph_export_rejects_unsupported_format(sample_graph_data):
    with pytest.raises(ValueError, match="Unsupported export format"):
        render_graph_export(sample_graph_data, "box", "#f0f0f0", "Arial", "dot", "jpg")
