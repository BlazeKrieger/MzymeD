#!/usr/bin/env python3
"""
Generate PyMOL visualization script with labeled interaction sites for real structures.
"""

from pathlib import Path


# Interaction sites from analysis
INTERACTIONS = {
    '2W52': [
        ('THR', 51), ('GLY', 49), ('GLY', 161), ('GLU', 107),
        ('TRP', 257), ('ASP', 256), ('PRO', 26), ('THR', 163),
        ('THR', 27), ('ASN', 43), ('ASP', 50), ('ASN', 162)
    ],
    '2W39': [
        ('GLU', 107), ('ASN', 43), ('TRP', 110), ('ALA', 101)
    ],
    '4BPZ': [
        ('ASP', 377), ('GLY', 189), ('GLU', 145), ('THR', 190),
        ('PHE', 146), ('GLU', 263), ('TRP', 264), ('TYR', 378), ('ALA', 240)
    ],
    '4BOW': [
        ('ASP', 295), ('ASP', 377), ('GLY', 189), ('GLU', 145),
        ('LEU', 292), ('ALA', 266), ('PHE', 146), ('THR', 190),
        ('SER', 290), ('TRP', 264), ('TYR', 378), ('GLU', 263),
        ('ALA', 240), ('HIS', 170)
    ]
}


def create_pymol_visualization_script(pdb_id: str, interactions: list, output_path: Path):
    """Create PyMOL script with labeled interaction sites."""
    
    # Create selection strings for interaction residues
    residue_selection = " or ".join([f"(resi {res_id} and resn {res_name})" 
                                      for res_name, res_id in interactions])
    
    script = f'''# PyMOL Visualization Script for {pdb_id}
# Real laminarinase-laminarin complex with labeled interaction sites

# Load structure
load real_structures/{pdb_id}.pdb

# Remove waters
remove solvent

# Color enzyme by secondary structure
hide everything
show cartoon
color wheat, polymer.protein
cartoon automatic
set cartoon_smooth_loops, 0

# Highlight substrate (heteroatoms)
select substrate, hetatm and not (resn NAG or resn MAN or resn BMA)
show sticks, substrate
color cyan, substrate
set stick_radius, 0.3, substrate

# Create selection for interaction sites
select interaction_sites, {residue_selection}
show sticks, interaction_sites
color red, interaction_sites
set stick_radius, 0.25, interaction_sites

# Label interaction residues
label interaction_sites and n. CA, "%s%s" % (resn, resi)
set label_color, red
set label_size, 14
set label_position, [0, 0, 3]

# Show hydrogen bonds
distance hbonds, substrate, interaction_sites, mode=2
hide labels, hbonds
color yellow, hbonds
set dash_width, 2

# Center view
center substrate
zoom substrate, 8

# Set background and lighting
bg_color white
set ray_trace_mode, 1
set antialias, 2
set ambient, 0.4
set direct, 0.6

# Optional: Save high-quality image
# ray 1600, 1200
# png {pdb_id}_labeled.png, dpi=300

print "="*60
print "Structure: {pdb_id}"
print "Interaction sites highlighted in RED"
print "Substrate highlighted in CYAN"
print "Yellow dashes show hydrogen bonds"
print "="*60
print ""
print "Controls:"
print "  - Rotate: Left mouse drag"
print "  - Zoom: Scroll wheel"
print "  - Pan: Middle mouse drag"
print "  - Toggle labels: disable/enable label"
print ""
print "Commands to try:"
print "  zoom interaction_sites  # Focus on binding site"
print "  hide labels             # Hide labels"
print "  show labels             # Show labels"
print "  ray 1600, 1200          # High-quality render"
'''
    
    output_path.write_text(script)
    print(f"✓ Created PyMOL script: {output_path.name}")


def main():
    base = Path(__file__).parent
    scripts_dir = base / "pymol_scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("GENERATING PYMOL VISUALIZATION SCRIPTS")
    print("=" * 80)
    
    for pdb_id, interactions in INTERACTIONS.items():
        print(f"\n{pdb_id}: {len(interactions)} interaction sites")
        output_path = scripts_dir / f"visualize_{pdb_id}.pml"
        create_pymol_visualization_script(pdb_id, interactions, output_path)
    
    # Create master script that shows all structures
    master_script = f'''# Master PyMOL script - Load all laminarinase-laminarin complexes

# Load all structures
load real_structures/2W52.pdb, lam16a_tri
load real_structures/2W39.pdb, lam16a_di
load real_structures/4BPZ.pdb, lama_tri
load real_structures/4BOW.pdb, lama_tetra

# Align all structures
alignto lam16a_tri

# Hide everything initially
hide everything

# Show all as cartoons
show cartoon, all
color wheat, all

# Show substrates
select all_substrates, hetatm and not (resn NAG or resn MAN or resn BMA or resn GOL or resn CA or resn NA)
show sticks, all_substrates
color cyan, lam16a_tri and all_substrates
color green, lam16a_di and all_substrates  
color magenta, lama_tri and all_substrates
color orange, lama_tetra and all_substrates
set stick_radius, 0.3, all_substrates

# Center and style
center all_substrates
zoom all_substrates, 10
bg_color white
set cartoon_transparency, 0.5

print "Loaded 4 laminarinase-laminarin structures:"
print "  lam16a_tri  - Laminarinase 16A + triose (cyan)"
print "  lam16a_di   - Laminarinase 16A + diose (green)"
print "  lama_tri    - LamA + triose (magenta)"
print "  lama_tetra  - LamA + tetraose (orange)"
'''
    
    master_path = scripts_dir / "visualize_all_complexes.pml"
    master_path.write_text(master_script)
    print(f"\n✓ Created master script: {master_path.name}")
    
    print(f"\n{'='*80}")
    print("✅ SCRIPTS GENERATED")
    print(f"{'='*80}")
    print(f"\nGenerated {len(INTERACTIONS) + 1} PyMOL scripts in: {scripts_dir}/")
    print("\n📌 To visualize:")
    print(f"   Individual: pymol pymol_scripts/visualize_2W52.pml")
    print(f"   All together: pymol pymol_scripts/visualize_all_complexes.pml")
    print("\n💡 Scripts automatically:")
    print("   - Label all interaction sites in RED")
    print("   - Highlight substrates in CYAN/colors")
    print("   - Show hydrogen bonds as yellow dashes")
    print("   - Center view on binding site")


if __name__ == "__main__":
    main()
