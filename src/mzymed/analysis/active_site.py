"""
Active site analysis and residue interaction identification.
"""

import numpy as np
from typing import List, Dict, Any, Optional


class ActiveSiteAnalyzer:
    """Analyze active sites and enzyme-substrate interactions."""
    
    def __init__(self):
        self.active_site_residues = []
        
    def identify_active_site(self, structure_data: Dict[str, Any], 
                            contact_threshold: float = 0.5) -> List[int]:
        """Identify active site residues based on contact predictions."""
        try:
            contacts = structure_data.get("contacts", None)
            if contacts is None:
                return []
            
            contact_scores = np.sum(contacts > contact_threshold, axis=1)
            active_site_indices = np.where(contact_scores > np.percentile(contact_scores, 75))[0]
            
            self.active_site_residues = active_site_indices.tolist()
            return self.active_site_residues
        except Exception as e:
            print(f"Error identifying active site: {e}")
            return []
    
    def analyze_interactions(self, enzyme_structure: Dict[str, Any],
                           substrate_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze enzyme-substrate interactions."""
        results = {
            "active_site_residues": self.active_site_residues,
            "interaction_strength": [],
            "key_contacts": []
        }
        
        try:
            if substrate_structure:
                enzyme_emb = enzyme_structure.get("embeddings")
                substrate_emb = substrate_structure.get("embeddings")
                
                if enzyme_emb is not None and substrate_emb is not None:
                    interaction_matrix = np.dot(enzyme_emb, substrate_emb.T)
                    strong_interactions = np.argwhere(
                        interaction_matrix > np.percentile(interaction_matrix, 90)
                    )
                    results["key_contacts"] = strong_interactions.tolist()
                    results["interaction_strength"] = np.max(interaction_matrix, axis=1).tolist()
            
            return results
        except Exception as e:
            print(f"Error analyzing interactions: {e}")
            return results
    
    def suggest_optimizations(self, analysis_results: Dict[str, Any],
                            sequence: str) -> List[Dict[str, Any]]:
        """Suggest residue mutations for optimizing interactions."""
        suggestions = []
        try:
            active_site = analysis_results.get("active_site_residues", [])
            interaction_strength = analysis_results.get("interaction_strength", [])
            
            for idx in active_site:
                if idx < len(sequence) and idx < len(interaction_strength):
                    current_aa = sequence[idx]
                    strength = interaction_strength[idx] if interaction_strength else 0
                    
                    if strength < 0.7:
                        suggestions.append({
                            "position": idx,
                            "original": current_aa,
                            "reason": "Low interaction strength at active site"
                        })
            
            return suggestions
        except Exception as e:
            print(f"Error suggesting optimizations: {e}")
            return suggestions