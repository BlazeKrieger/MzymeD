"""
Main MzymeD application for enzyme-substrate molecular dynamics analysis.
"""

import os
from typing import Optional, Dict, Any

from mzymed.file_handler import FileUploader
from mzymed.models.esm_predictor import ESM3Predictor
from mzymed.models.md_simulator import MDSimulator
from mzymed.analysis.active_site import ActiveSiteAnalyzer
from mzymed.visualization.visualizer import MolecularVisualizer


class MzymeDApp:
    """Main application for AI-powered enzyme-substrate molecular dynamics analysis."""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.file_uploader = FileUploader()
        self.esm_predictor = ESM3Predictor()
        self.md_simulator = MDSimulator(output_dir)
        self.analyzer = ActiveSiteAnalyzer()
        self.visualizer = MolecularVisualizer(output_dir)
        
        self.enzyme_structure = None
        self.substrate_structure = None

    def process_substrate(self, sequence_file: str) -> bool:
        """Process substrate sequence file (e.g., laminarin fragments)."""
        print(f"\n{'='*60}")
        print("PROCESSING SUBSTRATE")
        print(f"{'='*60}")

        is_valid, message = self.file_uploader.validate_sequence_file(sequence_file)
        if not is_valid:
            print(f"Error: {message}")
            return False

        print(f"✓ File validated: {message}")

        seq_record = self.file_uploader.load_sequence(sequence_file)
        if seq_record is None:
            return False

        sequence = str(seq_record.seq)
        print(f"✓ Loaded substrate sequence (length: {len(sequence)})")

        self.substrate_structure = self.esm_predictor.predict_structure(sequence, "substrate")
        if not self.substrate_structure:
            self.substrate_structure = {"sequence": sequence}

        return True
    
    def process_enzyme(self, sequence_file: str) -> bool:
        """Process enzyme sequence file."""
        print(f"\n{'='*60}")
        print("PROCESSING ENZYME")
        print(f"{'='*60}")
        
        is_valid, message = self.file_uploader.validate_sequence_file(sequence_file)
        if not is_valid:
            print(f"Error: {message}")
            return False
        
        print(f"✓ File validated: {message}")
        
        seq_record = self.file_uploader.load_sequence(sequence_file)
        if seq_record is None:
            return False
        
        sequence = str(seq_record.seq)
        print(f"✓ Loaded sequence (length: {len(sequence)})")
        
        self.enzyme_structure = self.esm_predictor.predict_structure(sequence, "enzyme")
        if not self.enzyme_structure:
            self.enzyme_structure = {"sequence": sequence}
        
        return True
    
    def analyze_interactions(self) -> Optional[Dict[str, Any]]:
        """Analyze enzyme-substrate interactions."""
        if self.enzyme_structure is None:
            return None
        
        print(f"\n{'='*60}")
        print("ANALYZING INTERACTIONS")
        print(f"{'='*60}")
        
        if "contacts" in self.enzyme_structure:
            active_site = self.analyzer.identify_active_site(self.enzyme_structure)
            print(f"✓ Found {len(active_site)} active site residues")
        
        results = self.analyzer.analyze_interactions(
            self.enzyme_structure, self.substrate_structure
        )

        if self.substrate_structure:
            binding_energy = self.md_simulator.calculate_binding_energy(
                self.enzyme_structure, self.substrate_structure
            )
            results["binding_energy"] = binding_energy
        
        return results
