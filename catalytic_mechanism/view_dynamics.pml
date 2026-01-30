# PyMOL Script: Realistic Laminarinase MD Simulation
# Shows 50-frame catalytic mechanism with enzyme dynamics

load "catalysis_dynamics.pdb", md

# Hide everything first
hide everything

# Show enzyme as cartoon (main visualization)
show cartoon, md and chain A
color spectrum, md and chain A

# Highlight catalytic residues as large, visible spheres
select cat_residues, (md and chain A and (resi 49 or resi 107 or resi 256 or resi 257))
show spheres, cat_residues
set sphere_scale, 0.6, cat_residues

color red, (md and chain A and resi 107)      # GLU107 - nucleophile
color orange, (md and chain A and resi 256)   # ASP256 - general acid
color yellow, (md and chain A and resi 257)   # TRP257 - binding
color purple, (md and chain A and resi 49)    # GLY49 - loop

# Show substrate/products (chain B, C, D) as prominent spheres
show spheres, md and chain B
show spheres, md and chain C
show spheres, md and chain D

color cyan, md and chain B      # Substrate
color green, md and chain C     # Product 1
color lime, md and chain D      # Product 2

set sphere_scale, 1.5, (md and chain B)
set sphere_scale, 1.5, (md and chain C)
set sphere_scale, 1.5, (md and chain D)

# Labels for catalytic residues
label (md and chain A and resi 107), "GLU107\nNucleophile"
label (md and chain A and resi 256), "ASP256\nGeneral Acid"
label (md and chain A and resi 257), "TRP257\nBinding"
label (md and chain A and resi 49), "GLY49\nLoop"

set label_color, black
set label_size, 14
set label_bg_color, white
set label_bg_outline, 1

# Lighting and rendering
bg_color white
set ambient, 1.0
set direct, 0.8
set reflect, 0.5
set specular, 1.0
set shininess, 50
set sphere_quality, 2
set cartoon_quality, 2
set antialias, 1

# Center on active site
center (md and chain A and resi 107)
zoom (md and chain A and (resi 49 or resi 107 or resi 256 or resi 257)), 8

# Animation settings
mset 1-50
set movie_fps, 10
mplay

# Print instructions
print ""
print "=========================================================================="
print "LAMINARINASE CATALYTIC MECHANISM - 50-FRAME MD SIMULATION"
print "=========================================================================="
print ""
print "FRAME BREAKDOWN (total runtime: 5 seconds at 10 fps):"
print "  Frames  1-9:  Substrate approaching enzyme (breathing dynamics)"
print "  Frames 10-19: Substrate entering active site (conformational change)"
print "  Frames 20-29: Michaelis complex formation (enzyme-substrate bound)"
print "  Frames 30-36: Nucleophilic attack by GLU107 (RED sphere)"
print "  Frames 37-43: ⚡ GLYCOSIDIC BOND CLEAVAGE (key mechanism step)"
print "  Frames 44-50: Product release and enzyme regeneration"
print ""
print "VISUALIZATION:"
print "  CARTOON (rainbow):  Full enzyme backbone with dynamics"
print "  RED SPHERE:         GLU107 - nucleophilic residue"
print "  ORANGE SPHERE:      ASP256 - general acid catalyst"
print "  YELLOW SPHERE:      TRP257 - substrate binding stabilization"
print "  PURPLE SPHERE:      GLY49 - active site loop"
print "  CYAN SPHERES:       Substrate (β-1,3-glucan) approaching"
print "  GREEN SPHERES:      Products after bond cleavage"
print ""
print "INTERACTIVE CONTROLS:"
print "  mplay       - Play animation from current frame"
print "  mstop       - Stop animation"
print "  mreverse    - Play backwards"
print "  frame N     - Jump to frame N (e.g., 'frame 25')"
print "  mset 1-50   - Show all frames 1-50"
print "  set movie_fps, 5  - Slow down (5 fps)"
print "  set movie_fps, 15 - Speed up (15 fps)"
print ""
print "MOUSE CONTROLS:"
print "  Scroll wheel     - Zoom in/out"
print "  Middle drag      - Rotate view"
print "  Right drag       - Translate"
print ""
print "=========================================================================="
print ""
