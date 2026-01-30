#!/usr/bin/env python3
"""
Generate a simple visual contact map for an enzyme (mock ESM predictor) and
write a PNG plus a brief JSON summary. Uses the laminarin substrate mock by default.
"""

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "src")
from mzymed.app import MzymeDApp


def plot_contacts(matrix: np.ndarray, title: str, out_path: Path) -> None:
    plt.figure(figsize=(6, 5))
    plt.imshow(matrix, cmap="viridis", origin="lower")
    plt.colorbar(label="Contact probability")
    plt.title(title)
    plt.xlabel("Residue j")
    plt.ylabel("Residue i")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=200)
    plt.close()


def main():
    base = Path(__file__).parent
    lam_dir = base / "laminarinases"
    substrate = base / "laminarin_substrate.fasta"

    # Pick a representative enzyme FASTA
    enzyme_file = lam_dir / "GH16" / "BxLam16A.fasta"
    if not enzyme_file.exists():
        raise SystemExit(f"Enzyme FASTA missing: {enzyme_file}")

    if not substrate.exists():
        raise SystemExit("Substrate FASTA missing: laminarin_substrate.fasta")

    app = MzymeDApp(output_dir="visual_outputs")

    if not app.process_enzyme(str(enzyme_file)):
        raise SystemExit("Failed to process enzyme")
    if not app.process_substrate(str(substrate)):
        raise SystemExit("Failed to process substrate")

    results = app.analyze_interactions() or {}
    contacts = app.enzyme_structure.get("contacts")

    if contacts is None:
        raise SystemExit("No contacts available from predictor")

    contact_mat = np.asarray(contacts)
    png_path = base / "visual_outputs" / "enzyme_contact_map.png"
    plot_contacts(contact_mat, f"Contacts: {enzyme_file.name}", png_path)

    summary = {
        "enzyme": enzyme_file.name,
        "substrate": substrate.name,
        "seq_length": app.enzyme_structure.get("length"),
        "active_site_residues": results.get("active_site_residues", []),
        "binding_energy": results.get("binding_energy"),
        "contact_png": str(png_path.relative_to(base)),
    }

    summary_path = base / "visual_outputs" / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("✓ Visual contact map written to", png_path)
    print("✓ Summary written to", summary_path)


if __name__ == "__main__":
    main()
