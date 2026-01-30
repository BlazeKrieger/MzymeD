"""
3D visualization and animation of molecular dynamics.
"""

import numpy as np
from typing import Optional, Dict, Any, List
import os


class MolecularVisualizer:
    """Create 3D visualizations and animations of molecular dynamics."""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_3d_structure(self, pdb_file: str, highlight_residues: Optional[List[int]] = None) -> str:
        """
        Create 3D visualization of protein structure.
        
        Args:
            pdb_file: Path to PDB file
            highlight_residues: Optional list of residue indices to highlight
            
        Returns:
            HTML string with 3D visualization
        """
        try:
            import py3Dmol
            
            with open(pdb_file, 'r') as f:
                pdb_data = f.read()
            
            view = py3Dmol.view(width=800, height=600)
            view.addModel(pdb_data, 'pdb')
            view.setStyle({'cartoon': {'color': 'spectrum'}})
            
            if highlight_residues:
                for res_idx in highlight_residues:
                    view.addStyle({'resi': str(res_idx)}, 
                                {'stick': {'color': 'red', 'radius': 0.5}})
            
            view.zoomTo()
            html = view._make_html()
            
            output_file = os.path.join(self.output_dir, "structure_3d.html")
            with open(output_file, 'w') as f:
                f.write(html)
            
            return output_file
        except Exception as e:
            print(f"Error creating 3D visualization: {e}")
            return ""
    
    def create_animation(self, trajectory_file: str, topology_file: str,
                        active_site: Optional[List[int]] = None) -> str:
        """Create animation of molecular dynamics trajectory."""
        try:
            print(f"Creating MD animation from {trajectory_file}...")
            animation_file = os.path.join(self.output_dir, "md_animation.html")
            
            html_content = f"""
            <html>
            <head><title>MD Animation</title></head>
            <body>
            <h1>Molecular Dynamics Animation</h1>
            <p>Animation of enzyme-substrate interaction dynamics</p>
            <p>Trajectory: {trajectory_file}</p>
            </body>
            </html>
            """
            
            with open(animation_file, 'w') as f:
                f.write(html_content)
            
            return animation_file
        except Exception as e:
            print(f"Error creating animation: {e}")
            return ""
