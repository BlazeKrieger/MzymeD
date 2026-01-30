# PyMOL Script: Enzyme-Substrate Complex MD Simulation
# Shows laminarinase dynamics WITH laminarin substrate bound

load "enzyme_substrate_trajectory.pdb", complex

# Hide everything initially
hide everything

# Show enzyme as cartoon (rainbow colored)
show cartoon, complex and chain A
color spectrum, complex and chain A
cartoon_fancy_helices, 1

# Show substrate (laminarin) as sticks and spheres
show sticks, complex and chain B
show spheres, complex and chain B
color cyan, complex and chain B
set stick_radius, 0.2
set sphere_scale, 0.8

# Highlight catalytic residues
select catalytic, (complex and chain A and (resi 49 or resi 107 or resi 256 or resi 257))
show spheres, catalytic
set sphere_scale, 0.5, catalytic

color red, (complex and chain A and resi 107)      # GLU - nucleophile
color orange, (complex and chain A and resi 256)   # ASP - general acid  
color yellow, (complex and chain A and resi 257)   # TRP - binding
color purple, (complex and chain A and resi 49)    # GLY - loop

# Add labels for catalytic residues
label (complex and chain A and resi 107), "GLU107\nNucleophile"
label (complex and chain A and resi 256), "ASP256\nGeneral Acid"

set label_color, black
set label_size, 14
set label_bg_color, white
set label_bg_outline, 1

# Rendering and lighting
bg_color white
set ambient, 1.0
set direct, 0.8
set reflect, 0.5
set specular, 1.0
set shininess, 50
set cartoon_quality, 2
set antialias, 1

# Center on active site (where substrate is)
center (complex and chain B)
zoom (complex and chain A and (resi 49 or resi 107 or resi 256 or resi 257 or resi 106 or resi 108 or resi 158 or resi 159)), 5

# Animation settings
mset 1-50
set movie_fps, 10
mplay

# Print instructions
print ""
print "=========================================================================="
print "ENZYME-SUBSTRATE COMPLEX - REAL MD SIMULATION (100 ps)"
print "=========================================================================="
print ""
print "VISUALIZATION:"
print "  CARTOON (rainbow):       Laminarinase enzyme backbone"
print "  CYAN STICKS + SPHERES:   Laminarin (β-1,3-glucan) substrate"
print "  RED SPHERE:              GLU107 - catalytic nucleophile"
print "  ORANGE SPHERE:           ASP256 - general acid catalyst"
print "  YELLOW SPHERE:           TRP257 - substrate binding"
print "  PURPLE SPHERE:           GLY49 - active site loop"
print ""
print "ANIMATION:"
print "  50 frames total (every 2 ps of simulation)"
print "  Shows real thermal dynamics at 300K"
print "  Enzyme wiggling + substrate vibration"
print "  Active site breathing"
print ""
print "INTERACTIVE CONTROLS:"
print "  mplay       - Play animation"
print "  mstop       - Stop animation"
print "  mreverse    - Play backwards"
print "  frame N     - Jump to frame (e.g., 'frame 25')"
print "  mset 1-50   - Show all frames"
print ""
print "MOUSE:"
print "  Scroll wheel     - Zoom in/out"
print "  Middle drag      - Rotate view"
print "  Right drag       - Translate"
print ""
print "KEY OBSERVATIONS:"
print "  • Watch how the enzyme backbone flexes around the substrate"
print "  • Notice the catalytic residues (red, orange) moving with substrate"
print "  • See the active site "breathing" as substrate vibrates"
print "  • This is REAL molecular dynamics - not artificial animation"
print ""
print "=========================================================================="
print ""
