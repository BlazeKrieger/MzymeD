#!/usr/bin/env python3
"""
Create an interactive 3D visualization of enzyme-substrate complex using Plotly.
This is much more reliable than 3Dmol and renders immediately.
"""

from pathlib import Path
import sys
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, "src")
from mzymed.file_handler import FileUploader
from mzymed.models.esm_predictor import ESM3Predictor


def helix_coords(length: int, radius: float = 8.0, rise: float = 1.5):
    coords = []
    for i in range(length):
        angle = i * 2 * np.pi / 10.0
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = i * rise
        coords.append((x, y, z))
    return np.array(coords)


def substrate_coords(length: int, radius: float = 15.0):
    coords = []
    for i in range(length):
        angle = i * 0.5
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 2.0 * np.sin(angle * 2)
        coords.append((x, y, z))
    return np.array(coords)


def create_3d_plot(enzyme_seq: str, substrate_seq: str, output_path: Path):
    """Create interactive Plotly 3D visualization."""
    
    # Generate coordinates
    enz_coords = helix_coords(len(enzyme_seq))
    sub_coords = substrate_coords(len(substrate_seq))
    
    # Center the structure
    all_coords = np.vstack([enz_coords, sub_coords])
    center = all_coords.mean(axis=0)
    enz_coords -= center
    sub_coords -= center
    
    # Create figure
    fig = go.Figure()
    
    # Add enzyme (chain A) - red spheres
    fig.add_trace(go.Scatter3d(
        x=enz_coords[:, 0],
        y=enz_coords[:, 1],
        z=enz_coords[:, 2],
        mode='markers+lines',
        name='Enzyme (Chain A)',
        marker=dict(size=6, color='red', opacity=0.8),
        line=dict(color='red', width=2),
        hovertemplate='<b>Enzyme</b><br>Pos: (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>'
    ))
    
    # Add substrate (chain B) - cyan spheres
    fig.add_trace(go.Scatter3d(
        x=sub_coords[:, 0],
        y=sub_coords[:, 1],
        z=sub_coords[:, 2],
        mode='markers+lines',
        name='Substrate (Chain B)',
        marker=dict(size=5, color='cyan', opacity=0.8),
        line=dict(color='cyan', width=2),
        hovertemplate='<b>Substrate</b><br>Pos: (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='<b>Enzyme-Substrate Complex</b><br>BxLam16A (laminarinase) + Laminarin Mock',
        scene=dict(
            xaxis_title='X (Å)',
            yaxis_title='Y (Å)',
            zaxis_title='Z (Å)',
            bgcolor='rgba(240, 240, 240, 1)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        width=1000,
        height=800,
        hovermode='closest',
        showlegend=True
    )
    
    # Save as HTML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f"✓ Saved interactive 3D plot to {output_path}")
    
    return fig


def main():
    base = Path(__file__).parent
    enzyme_path = base / "laminarinases" / "GH16" / "BxLam16A.fasta"
    substrate_path = base / "laminarin_substrate.fasta"
    
    # Load sequences
    uploader = FileUploader()
    enzyme_rec = uploader.load_sequence(str(enzyme_path))
    substrate_rec = uploader.load_sequence(str(substrate_path))
    
    if not enzyme_rec or not substrate_rec:
        raise ValueError("Failed to load sequences")
    
    enzyme_seq = str(enzyme_rec.seq)
    substrate_seq = str(substrate_rec.seq)
    
    # Create visualization
    output_html = base / "visual_outputs" / "enzyme_substrate_3d.html"
    create_3d_plot(enzyme_seq, substrate_seq, output_html)
    
    print(f"\n✓ Created 3D visualization")
    print(f"  Enzyme: {enzyme_path.name} ({len(enzyme_seq)} aa)")
    print(f"  Substrate: {substrate_path.name} ({len(substrate_seq)} aa)")
    print(f"\nOpen in browser: {output_html}")


if __name__ == "__main__":
    main()
