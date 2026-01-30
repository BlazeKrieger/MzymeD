# Master PyMOL script - Load all laminarinase-laminarin complexes

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
