"""Setup file for MzymeD package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mzymed",
    version="0.1.0",
    author="MzymeD Team",
    description="AI-Powered Tool for Enzyme-Substrate Molecular Dynamics Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlazeKrieger/MzymeD",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "biopython>=1.79",
        "numpy>=1.21.0",
        "flask>=2.3.0",
    ],
    extras_require={
        "full": [
            "torch>=2.0.0",
            "esm",
            "MDAnalysis>=2.0.0",
            "py3Dmol>=2.0.0",
            "plotly>=5.0.0",
        ],
    },
)
