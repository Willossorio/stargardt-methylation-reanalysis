"""
Process all 24 raw IDAT samples through methylprep to produce our own,
independently-computed beta value matrix (rather than relying solely on the
authors' processed values from the GEO series matrix).

Run from repo root: .venv/bin/python src/run_pipeline.py
"""
from pathlib import Path

import methylprep

OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    betas = methylprep.run_pipeline(
        "data/raw/idat",
        betas=True,
        export=False,
    )
    out_path = OUT_DIR / "beta_values_ours.csv"
    betas.to_csv(out_path)
    print(f"Wrote {out_path}: {betas.shape[0]} probes x {betas.shape[1]} samples")


if __name__ == "__main__":
    main()
