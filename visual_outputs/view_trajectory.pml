# PyMOL script for MD trajectory visualization
# Load trajectory
load "md_trajectory.pdb", traj

# Split chains
select enzyme, chain A
select substrate, chain B

# Set enzyme representation
show cartoon, enzyme
color red, enzyme
cartoon helix, enzyme
set cartoon_transparency, 0.3, enzyme

# Set substrate representation
show spheres, substrate
color cyan, substrate
set sphere_scale, 0.8, substrate

# Center and zoom
center
zoom

# Animation settings
set movie_loop, 1
set movie_fps, 10
mplay

# Optional: High-quality rendering
set ray_trace_mode, 1
set antialias, 2
bg_color white

# Optional: Save animation frames (uncomment to use)
# mset 1 x20
# frame 1
# mpng trajectory_frames/frame_, width=1200, height=900

print "MD Trajectory loaded!"
print "Use: mplay to play animation"
print "Use: mstop to stop"
print "Frames: 20"
print "Enzyme (red): BxLam16A laminarinase"
print "Substrate (cyan): Laminarin approaching active site"
