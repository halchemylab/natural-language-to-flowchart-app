import cairosvg
from io import BytesIO

def svg_to_pdf(svg_string: str) -> bytes:
    """Converts an SVG string to PDF bytes using CairoSVG."""
    return cairosvg.svg2pdf(bytestring=svg_string.encode('utf-8'))

def svg_to_png(svg_string: str) -> bytes:
    """Converts an SVG string to PNG bytes using CairoSVG."""
    return cairosvg.svg2png(bytestring=svg_string.encode('utf-8'))
