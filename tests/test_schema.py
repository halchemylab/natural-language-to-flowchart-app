import pytest
import json
from pydantic import ValidationError

from graph_schema import Graph, Node


@pytest.fixture
def valid_graph_data():
    """Provides a valid graph structure as a dictionary."""
    return {
        "nodes": [
            {"id": "A", "label": "Start"},
            {"id": "B", "label": "End", "shape": "ellipse"}
        ],
        "edges": [
            {"source": "A", "target": "B", "label": "connects"}
        ],
        "layout": {"direction": "LR"}
    }


@pytest.fixture
def sample_json_path():
    """Returns the path to the sample JSON file."""
    import os
    return os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'sample.json')


def test_valid_graph_instantiation(valid_graph_data):
    """Tests that a valid graph dictionary can be successfully parsed."""
    try:
        graph = Graph.model_validate(valid_graph_data)
        assert len(graph.nodes) == 2
        assert graph.nodes[0].id == "A"
        assert graph.nodes[1].shape == "ellipse" # Check default override
        assert len(graph.edges) == 1
        assert graph.layout.direction == "LR"
    except ValidationError as e:
        pytest.fail(f"Valid graph data failed validation: {e}")


def test_missing_nodes_fails():
    """Tests that a graph with no nodes fails validation."""
    with pytest.raises(ValidationError):
        Graph.model_validate({"nodes": [], "edges": []})


def test_invalid_node_shape_fails(valid_graph_data):
    """Tests that an unsupported node shape raises a validation error."""
    valid_graph_data["nodes"][0]["shape"] = "hexagon" # Invalid shape
    with pytest.raises(ValidationError):
        Graph.model_validate(valid_graph_data)


def test_invalid_layout_direction_fails(valid_graph_data):
    """Tests that an unsupported layout direction fails validation."""
    valid_graph_data["layout"]["direction"] = "UP" # Invalid direction
    with pytest.raises(ValidationError):
        Graph.model_validate(valid_graph_data)


def test_edge_with_nonexistent_node_fails(valid_graph_data):
    """Tests that an edge pointing to a non-existent node ID fails."""
    valid_graph_data["edges"][0]["target"] = "Z" # Node 'Z' does not exist
    with pytest.raises(ValueError, match="does not match any node ID"):
        Graph.model_validate(valid_graph_data)


def test_default_values_are_applied():
    """Checks that default values are correctly applied to nodes and layout."""
    data = {
        "nodes": [{"id": "1", "label": "Only ID and Label"}],
        "edges": []
    }
    graph = Graph.model_validate(data)
    assert graph.nodes[0].shape == "box" # Default shape
    assert graph.nodes[0].group == "default" # Default group
    assert graph.layout.direction == "TB" # Default layout direction


def test_sample_file_is_valid(sample_json_path):
    """Validates the provided sample.json file against the schema."""
    with open(sample_json_path, 'r') as f:
        data = json.load(f)
    
    try:
        Graph.model_validate(data)
    except ValidationError as e:
        pytest.fail(f"sample.json failed validation: {e}")
