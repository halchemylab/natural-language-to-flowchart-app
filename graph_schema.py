from pydantic import BaseModel, Field, field_validator, model_validator, conlist
from typing import Literal, List
import logging

# --- Constants ---
ALLOWED_SHAPES = ["box", "ellipse", "diamond", "circle"]
ALLOWED_DIRECTIONS = ["LR", "TB"]

# --- Pydantic Models for Graph Schema Validation ---

class Node(BaseModel):
    """Represents a single node in the graph."""
    id: str = Field(..., description="A short, unique identifier for the node (e.g., 'A', 'B', 'Start').")
    label: str = Field(..., max_length=100, description="The text label displayed on the node (max 6 words recommended).")
    group: str = Field(default="default", description="A group name for styling or filtering.")
    shape: Literal[*ALLOWED_SHAPES] = Field(default="box", description="The shape of the node.")

    @field_validator('label')
    def label_word_count(cls, v):
        if len(v.split()) > 10:
            logging.warning(f"Node label '{v}' is long ({len(v.split())} words). Consider shortening it.")
        return v

class Edge(BaseModel):
    """Represents a directed edge (connection) between two nodes."""
    source: str = Field(..., description="The ID of the source node.")
    target: str = Field(..., description="The ID of the target node.")
    label: str | None = Field(default=None, max_length=50, description="An optional label for the edge.")

class Layout(BaseModel):
    """Defines the overall layout direction of the graph."""
    direction: Literal[*ALLOWED_DIRECTIONS] = Field(default="TB", description="The direction of the graph layout (Top-to-Bottom or Left-to-Right).")

class Graph(BaseModel):
    """The root model for the entire graph structure."""
    nodes: conlist(Node, min_length=1, max_length=100) = Field(..., description="A list of all nodes in the graph.")
    edges: List[Edge] = Field(default=[], description="A list of all edges connecting the nodes.")
    layout: Layout = Field(default_factory=Layout, description="Graph layout configuration.")

    @model_validator(mode='after')
    def check_edge_node_ids_exist(self) -> 'Graph':
        """Ensures that every edge connects to valid nodes."""
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                raise ValueError(f"Edge source '{edge.source}' does not match any node ID.")
            if edge.target not in node_ids:
                raise ValueError(f"Edge target '{edge.target}' does not match any node ID.")
        return self
