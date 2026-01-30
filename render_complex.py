#!/usr/bin/env python3
"""
Render enzyme-substrate complex and save as PNG image
"""

from pymol import cmd, finish_launching
import os

print("\n" + "="*70)
print("RENDERING ENZYME-SUBSTRATE COMPLEX")
print("="*70 + "\n")

# Initialize PyMOL
finish_launching()

# Load structure
print("1. Loading enzyme_substrate_combined.pdb...")
cmd.load('md_simulation/enzyme_substrate_combined.pdb')

# Hide everything
print("2. Applying visualization settings...")
cmd.hide('all')

# Show enzyme
cmd.show('cartoon', 'chain A')
cmd.color('blue', 'chain A')

# Show substrate
cmd.show('sticks', 'chain B+C+D')
cmd.color('cyan', 'chain B+C+D')

# Highlight catalytic residues
cmd.show('spheres', 'resi 107 or resi 256 or resi 257 or resi 49')
cmd.color('red', 'resi 107')
cmd.color('orange', 'resi 256')
cmd.color('yellow', 'resi 257')
cmd.color('purple', 'resi 49')

# Style
cmd.set('sphere_scale', 0.5)
cmd.set('cartoon_loop_radius', 0.3)

# Background
cmd.bg_color('white')
cmd.set('ray_opaque_background', 1)

# Lighting
cmd.set('light_count', 5)
cmd.set('ambient', 1.0)
cmd.set('direct', 1.0)

# View
print("3. Centering on active site...")
cmd.center('resi 107')
cmd.zoom('resi 100-260', 5)
cmd.reset()

# Render
print("4. Rendering high-quality image...")
os.makedirs('md_simulation', exist_ok=True)
cmd.ray(1920, 1080)
cmd.png('md_simulation/enzyme_substrate_complex.png')

print("\n✓ Image saved: md_simulation/enzyme_substrate_complex.png")
print(f"   Resolution: 1920x1080 pixels")
print(f"   Quality: Ray-traced rendering")

# Save state
cmd.save('md_simulation/enzyme_substrate_session.pse')
print(f"   Session saved: md_simulation/enzyme_substrate_session.pse")

print("\n✓ COMPLETE!")
