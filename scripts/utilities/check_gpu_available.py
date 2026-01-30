#!/usr/bin/env python3
"""Check available OpenMM platforms."""
from openmm import Platform

print("\n" + "="*60)
print("OPENMM PLATFORM DIAGNOSTICS")
print("="*60)

platforms = []
for platform in ["Reference", "CPU", "CUDA", "OpenCL"]:
    try:
        p = Platform.getPlatformByName(platform)
        platforms.append((platform, "Available"))
        print(f"✓ {platform:12s} - Available")
    except Exception as e:
        platforms.append((platform, f"NOT available: {str(e)[:50]}"))
        print(f"✗ {platform:12s} - {str(e)[:80]}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

cuda_available = any(p[0] == "CUDA" and "Available" in p[1] for p in platforms)
gpu_available = any("GPU" in p[1] or p[0] in ["CUDA", "OpenCL"] and "Available" in p[1] for p in platforms)

if cuda_available:
    print("✓ CUDA GPU available - Simulations will use GPU")
elif gpu_available:
    print("✓ GPU available (OpenCL) - Simulations will use GPU")
else:
    print("✗ NO GPU PLATFORMS DETECTED")
    print("\nTo enable GPU:")
    print("  conda install -c conda-forge openmm-cuda::11.8 cuda-toolkit::11.8")
    print("  Or for OpenCL:")
    print("  conda install -c conda-forge openmm-opencl")

print("\n" + "="*60)
