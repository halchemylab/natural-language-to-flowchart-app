from pydantic import BaseModel, Field, validator, conlist
from typing import Literal, List

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

    @validator('label')
    def label_word_count(cls, v):
        if len(v.split()) > 10: # A soft warning, but let's be more lenient than 6
            # In a real app, you might log this instead of raising an error
            # For now, we'll allow it but it's good practice to check
            pass
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

    @validator('edges')
    def check_edge_node_ids_exist(cls, edges, values):
        """Ensures that every edge connects to valid nodes."""
        if 'nodes' not in values:
            # This can happen if nodes validation fails first
            return edges
            
        node_ids = {node.id for node in values['nodes']}
        for edge in edges:
            if edge.source not in node_ids:
                raise ValueError(f"Edge source '{edge.source}' does not match any node ID.")
            if edge.target not in node_ids:
                raise ValueError(f"Edge target '{edge.target}' does not match any node ID.")
        return edges
