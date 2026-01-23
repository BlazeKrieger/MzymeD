#!/usr/bin/env python3
"""
ColabFold batch prediction runner for enzyme structures.
Submits all sequences from a FASTA file to ColabFold for prediction.
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Run ColabFold batch prediction on enzyme FASTA sequences"
    )
    parser.add_argument(
        "fasta",
        type=str,
        help="Path to input FASTA file with enzyme sequences"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output directory for predictions"
    )
    parser.add_argument(
        "--num-models",
        type=int,
        default=1,
        help="Number of model ensembles to run (default: 1 for low VRAM)"
    )
    parser.add_argument(
        "--num-recycle",
        type=int,
        default=3,
        help="Number of recycles (default: 3)"
    )
    parser.add_argument(
        "--gpu-relax",
        action="store_true",
        help="Enable GPU-based relaxation (requires ~16 GB VRAM)"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="alphafold2_ptm",
        help="Model type: alphafold2_ptm (monomer) or alphafold2_multimer_v3 (complex)"
    )
    
    args = parser.parse_args()
    
    # Import ColabFold after args are parsed (fails gracefully if not installed)
    try:
        from colabfold.batch import run
    except ImportError:
        print("Error: ColabFold not installed. Install via: pip install colabfold")
        sys.exit(1)
    
    fasta_path = Path(args.fasta).resolve()
    output_dir = Path(args.output).resolve()
    
    # Validate input
    if not fasta_path.exists():
        print(f"Error: FASTA file not found: {fasta_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Running ColabFold batch prediction")
    print(f"  Input:  {fasta_path}")
    print(f"  Output: {output_dir}")
    print(f"  Models: {args.num_models}, Recycles: {args.num_recycle}")
    print(f"  GPU Relax: {args.gpu_relax}")
    
    # Run ColabFold batch prediction
    try:
        run(
            fasta_file=str(fasta_path),
            out_dir=str(output_dir),
            num_models=args.num_models,
            num_recycles=args.num_recycle,
            use_gpu_relax=args.gpu_relax,
            model_type=args.model_type,
            amber_relax=not args.gpu_relax,
            zip_results=False,
            save_single_representations=False,
            save_all=False,
            is_complex=("multimer" in args.model_type),
        )
        print(f"\nCompleted! Results in {output_dir}")
    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
