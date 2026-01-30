# PyMOL Visualization Script for 2W39
# Real laminarinase-laminarin complex with labeled interaction sites

# Load structure
load real_structures/2W39.pdb

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
select interaction_sites, (resi 107 and resn GLU) or (resi 43 and resn ASN) or (resi 110 and resn TRP) or (resi 101 and resn ALA)
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
# png 2W39_labeled.png, dpi=300

print "="*60
print "Structure: 2W39"
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
