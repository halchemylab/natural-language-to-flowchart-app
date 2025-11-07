import pytest
from unittest.mock import MagicMock, patch
from openai import RateLimitError, APIError
from pydantic import ValidationError
import json

from llm_client import generate_graph_from_text, GraphGenerationError
from graph_schema import Graph

@pytest.fixture
def mock_openai_client():
    with patch("llm_client.OpenAI") as mock_openai:
        yield mock_openai

def test_generate_graph_from_text_success(mock_openai_client):
    # Arrange
    mock_client = MagicMock()
    mock_openai_client.return_value = mock_client

    valid_graph_data = {
        "nodes": [{"id": "A", "label": "Start"}],
        "edges": []
    }
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(valid_graph_data)
    mock_response.usage.total_tokens = 100
    mock_client.chat.completions.create.return_value = mock_response

    # Act
    graph = generate_graph_from_text("test_api_key", "test prompt")

    # Assert
    assert isinstance(graph, Graph)
    assert graph.nodes[0].id == "A"
    mock_client.chat.completions.create.assert_called_once()

def test_generate_graph_from_text_invalid_json_retry(mock_openai_client):
    # Arrange
    mock_client = MagicMock()
    mock_openai_client.return_value = mock_client

    invalid_json_response = MagicMock()
    invalid_json_response.choices[0].message.content = "this is not json"
    invalid_json_response.usage.total_tokens = 50

    valid_graph_data = {
        "nodes": [{"id": "B", "label": "Valid"}],
        "edges": []
    }
    valid_response = MagicMock()
    valid_response.choices[0].message.content = json.dumps(valid_graph_data)
    valid_response.usage.total_tokens = 100

    mock_client.chat.completions.create.side_effect = [invalid_json_response, valid_response]

    # Act
    graph = generate_graph_from_text("test_api_key", "test prompt")

    # Assert
    assert isinstance(graph, Graph)
    assert graph.nodes[0].id == "B"
    assert mock_client.chat.completions.create.call_count == 2

def test_generate_graph_from_text_validation_error_retry(mock_openai_client):
    # Arrange
    mock_client = MagicMock()
    mock_openai_client.return_value = mock_client

    invalid_schema_data = {"nodes": [{"id": "C"}]} # Missing 'label'
    invalid_schema_response = MagicMock()
    invalid_schema_response.choices[0].message.content = json.dumps(invalid_schema_data)
    invalid_schema_response.usage.total_tokens = 75

    valid_graph_data = {
        "nodes": [{"id": "D", "label": "Correct"}],
        "edges": []
    }
    valid_response = MagicMock()
    valid_response.choices[0].message.content = json.dumps(valid_graph_data)
    valid_response.usage.total_tokens = 100

    mock_client.chat.completions.create.side_effect = [invalid_schema_response, valid_response]

    # Act
    graph = generate_graph_from_text("test_api_key", "test prompt")

    # Assert
    assert isinstance(graph, Graph)
    assert graph.nodes[0].id == "D"
    assert mock_client.chat.completions.create.call_count == 2

def test_generate_graph_from_text_rate_limit_error(mock_openai_client):
    # Arrange
    mock_client = MagicMock()
    mock_openai_client.return_value = mock_client
    mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded", response=MagicMock(), body=None)

    # Act & Assert
    with pytest.raises(GraphGenerationError, match="API error after multiple retries"):
        generate_graph_from_text("test_api_key", "test prompt", max_retries=1)
    
    assert mock_client.chat.completions.create.call_count == 2

def test_generate_graph_from_text_api_error(mock_openai_client):
    # Arrange
    mock_client = MagicMock()
    mock_openai_client.return_value = mock_client
    mock_client.chat.completions.create.side_effect = APIError("API error", request=MagicMock(), body=None)

    # Act & Assert
    with pytest.raises(GraphGenerationError, match="API error after multiple retries"):
        generate_graph_from_text("test_api_key", "test prompt", max_retries=1)

    assert mock_client.chat.completions.create.call_count == 2

def test_generate_graph_from_text_fails_after_max_retries(mock_openai_client):
    # Arrange
    mock_client = MagicMock()
    mock_openai_client.return_value = mock_client

    invalid_response = MagicMock()
    invalid_response.choices[0].message.content = "invalid"
    mock_client.chat.completions.create.return_value = invalid_response

    # Act & Assert
    with pytest.raises(GraphGenerationError, match="Failed to generate a valid graph after multiple attempts."):
        generate_graph_from_text("test_api_key", "test prompt", max_retries=2)
    
    assert mock_client.chat.completions.create.call_count == 3
