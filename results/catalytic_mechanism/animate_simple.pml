# Simple PyMOL animation - shows enzyme and mechanism
load "laminarinase_catalysis.pdb", mech

# Show all atoms in white first
show sticks
color white

# Show enzyme as cartoon
show cartoon, mech and chain A
color spectrum, mech and chain A

# Show substrate (chain B) as large cyan spheres
show spheres, mech and chain B
color cyan, mech and chain B
set sphere_scale, 2.0, mech and chain B

# Highlight key residues on enzyme as red spheres
show spheres, (mech and chain A and (resi 107 or resi 256 or resi 257 or resi 49))
set sphere_scale, 0.4, (mech and chain A and (resi 107 or resi 256 or resi 257 or resi 49))
color red, (mech and chain A and resi 107)
color orange, (mech and chain A and resi 256)
color yellow, (mech and chain A and resi 257)
color purple, (mech and chain A and resi 49)

# Set white background and good lighting
bg_color white
set ambient, 1.0
set direct, 0.8
set specular, 1.0
set sphere_quality, 2

# Reset view and zoom to all
reset
zoom
mset 1-30
framerate 4
mplay

print "Animation loaded!"
print "CYAN spheres = substrate (moving across frames)"
print "COLORED spheres on protein = catalytic residues"
print "Use: mplay (play), mstop (stop), frame N (goto frame)"
