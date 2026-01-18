# PyMOL script for enzyme-substrate visualization
# Load structures
load "enzyme.pdb", enzyme
load "substrate.pdb", substrate

# Set styles
show cartoon, enzyme
color red, enzyme
cartoon helix, enzyme

show sticks, substrate
color cyan, substrate

# Set representation
as spheres, enzyme
as spheres, substrate
set sphere_scale, 0.6, enzyme
set sphere_scale, 0.5, substrate

# Coloring
color red, enzyme
color cyan, substrate

# Center and zoom
center
zoom

# Fancy rendering (optional - comment out if slow)
set ray_trace_mode, 1
set antialias, 2

# Set background
bg_color white

# Save image
# ray 1200, 900
# png enzyme_substrate_md.png, dpi=300

print "Enzyme-substrate complex loaded!"
print "Enzyme (red): BxLam16A laminarinase"
print "Substrate (cyan): Laminarin mock"
