# PyMOL Animation: Laminarinase Catalytic Mechanism
# Shows glycosidic bond cleavage by catalytic residues

load "laminarinase_catalysis.pdb", mechanism

# Clear any previous selections
hide everything, all

# Show the enzyme as cartoon (main structure)
show cartoon, mechanism and chain A
color spectrum, mechanism and chain A
cartoon_fancy_helices, 1

# Highlight catalytic residues as spheres overlaid on cartoon
select catalytic, (mechanism and chain A and (resi 107 or resi 256 or resi 257 or resi 49))
show spheres, catalytic
set sphere_scale, 0.5, catalytic

# Color catalytic residues distinctly
color red, (mechanism and chain A and resi 107)      # GLU - nucleophile
color orange, (mechanism and chain A and resi 256)   # ASP - general acid
color yellow, (mechanism and chain A and resi 257)   # TRP - binding
color purple, (mechanism and chain A and resi 49)    # GLY - loop

# Show substrate/products as prominent spheres (chain B)
select substrate, (mechanism and chain B and resn GLC)
show spheres, substrate
color cyan, substrate
set sphere_scale, 1.2, substrate

# Add labels for key residues
set label_bg_color, white
set label_bg_outline, 1
label (mechanism and chain A and resi 107), "GLU107\nNucleophile",
label (mechanism and chain A and resi 256), "ASP256\nGeneral Acid",
label (mechanism and chain A and resi 257), "TRP257\nBinding",
set label_color, black
set label_size, 16
set label_outline_color, white

# Rendering settings - CRITICAL FOR VISIBILITY
bg_color white
set ambient, 1.0
set direct, 0.8
set reflect, 0.4
set specular, 1.0
set shininess, 50
set sphere_quality, 3
set cartoon_quality, 2
set antialias, 1

# Center on enzyme active site
center (mechanism and chain A and resi 107)
zoom (mechanism and chain A and (resi 49 or resi 107 or resi 256 or resi 257)), 5

# Animation playback
mset 1-30
framerate 5
mplay

# Print mechanism details
print ""
print "================================================================"
print "LAMINARINASE CATALYTIC MECHANISM ANIMATION"
print "================================================================"
print ""
print "FRAME BREAKDOWN:"
print "  Frames 1-6:   Substrate approach (CYAN spheres moving toward enzyme)"
print "  Frames 7-16:  Substrate binding in active site"
print "  Frames 17-21: Nucleophilic attack by GLU107 (RED)"
print "                General acid assistance from ASP256 (ORANGE)"
print "  Frames 22-26: GLYCOSIDIC BOND CLEAVAGE (⚡ key mechanism event)"
print "  Frames 27-30: Product release from active site"
print ""
print "CATALYTIC RESIDUES (highlighted as spheres):"
print "  RED:    GLU107 - Nucleophile (attacks C1 of substrate)"
print "  ORANGE: ASP256 - General acid catalyst"
print "  YELLOW: TRP257 - Substrate binding and positioning"
print "  PURPLE: GLY49 - Active site loop"
print ""
print "INTERACTIVE CONTROLS:"
print "  mplay       - Play animation forward"
print "  mstop       - Stop animation"
print "  mreverse    - Play backwards"
print "  frame N     - Jump to frame N"
print "  mset 1-30   - Show frames 1-30"
print ""
print "Use mouse scroll to zoom, middle-drag to rotate"
print "================================================================"
print ""
