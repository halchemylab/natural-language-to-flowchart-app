import argparse
import json
import os
from graph_schema import Graph
from utils.export import svg_to_pdf, svg_to_png

# A simple SVG template for CLI export
SVG_TEMPLATE = '''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        .node {{ fill: #97C2FC; stroke: #2B7CE9; stroke-width: 2px; }}
        .label {{ font-family: sans-serif; font-size: 14px; text-anchor: middle; }}
    </style>
    {elements}
</svg>'''

def render_graph_to_svg(graph: Graph) -> str:
    """A very basic SVG renderer for the CLI tool."""
    elements = []
    width, height = 800, 600 # default size
    positions = {}
    
    # Simple grid layout
    x, y, col_count = 50, 50, 4
    for i, node in enumerate(graph.nodes):
        positions[node.id] = (x, y)
        elements.append(f'<rect x="{x-40}" y="{y-20}" width="80" height="40" rx="5" class="node" />')
        elements.append(f'<text x="{x}" y="{y+5}" class="label">{node.label}</text>')
        x += 150
        if (i + 1) % col_count == 0:
            x = 50
            y += 100

    for edge in graph.edges:
        start_pos = positions.get(edge.source)
        end_pos = positions.get(edge.target)
        if start_pos and end_pos:
            elements.append(f'<line x1="{start_pos[0]}" y1="{start_pos[1]}" x2="{end_pos[0]}" y2="{end_pos[1]}" stroke="#848484" stroke-width="2" marker-end="url(#arrow)" />')

    # Define arrowhead marker
    marker = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" /></marker></defs>'
    elements.insert(0, marker)

    return SVG_TEMPLATE.format(width=width, height=y+50, elements="\n".join(elements))

def main():
    parser = argparse.ArgumentParser(description="Convert GRAPH JSON to an image or PDF.")
    parser.add_argument("input_file", help="Path to the input GRAPH JSON file.")
    parser.add_argument("output_file", help="Path to the output file (e.g., output.svg, output.pdf, output.png).")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found at {args.input_file}")
        return

    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(args.input_file, 'r') as f:
        try:
            data = json.load(f)
            graph = Graph.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error: Invalid GRAPH JSON file. {e}")
            return

    svg_content = render_graph_to_svg(graph)
    output_ext = os.path.splitext(args.output_file)[1].lower()

    if output_ext == ".svg":
        with open(args.output_file, "w") as f:
            f.write(svg_content)
        print(f"Successfully exported to {args.output_file}")
    elif output_ext == ".pdf":
        pdf_bytes = svg_to_pdf(svg_content)
        with open(args.output_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"Successfully exported to {args.output_file}")
    elif output_ext == ".png":
        png_bytes = svg_to_png(svg_content)
        with open(args.output_file, "wb") as f:
            f.write(png_bytes)
        print(f"Successfully exported to {args.output_file}")
    else:
        print(f"Error: Unsupported output format '{output_ext}'. Please use .svg, .pdf, or .png.")

if __name__ == "__main__":
    main()
