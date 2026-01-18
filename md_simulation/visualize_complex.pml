# PyMOL visualization script for enzyme-substrate complex
# Hide everything first
hide all

# Show enzyme as rainbow cartoon
show cartoon, chain A
color spectrum, chain A

# Show substrate as cyan sticks
show sticks, chain B+C+D
color cyan, chain B+C+D

# Highlight catalytic residues
show spheres, resi 107 or resi 256 or resi 257 or resi 49
color red, resi 107
color orange, resi 256
color yellow, resi 257
color purple, resi 49

# Set style
set sphere_scale, 0.5
set cartoon_loop_radius, 0.3

# Background
bg_color white
set ray_opaque_background, 1

# View and lighting
reset
set light_count, 5
set ambient, 1.0
set direct, 1.0

# Center on active site
center resi 107
zoom resi 100-260, 5

print "Visualization ready!"
print "Press 'Play' button or type 'mplay' to see animation"
