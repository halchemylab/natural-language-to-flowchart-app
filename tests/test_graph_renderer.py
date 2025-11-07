import pytest
from graphviz import Digraph
from ui.graph_renderer import create_graphviz_chart

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
