# PyMOL Visualization Script for 4BOW
# Real laminarinase-laminarin complex with labeled interaction sites

# Load structure
load real_structures/4BOW.pdb

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
select interaction_sites, (resi 295 and resn ASP) or (resi 377 and resn ASP) or (resi 189 and resn GLY) or (resi 145 and resn GLU) or (resi 292 and resn LEU) or (resi 266 and resn ALA) or (resi 146 and resn PHE) or (resi 190 and resn THR) or (resi 290 and resn SER) or (resi 264 and resn TRP) or (resi 378 and resn TYR) or (resi 263 and resn GLU) or (resi 240 and resn ALA) or (resi 170 and resn HIS)
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
# png 4BOW_labeled.png, dpi=300

print "="*60
print "Structure: 4BOW"
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
