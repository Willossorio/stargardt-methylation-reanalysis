"""
Parse the GSE147436 series matrix header and build:
  1. data/processed/sample_sheet.csv - metadata per sample (methylprep-compatible)
  2. A quick printed inventory of the raw IDAT files on disk.

Run from repo root: .venv/bin/python src/build_sample_sheet.py
"""
import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
SERIES_MATRIX = RAW_DIR / "GSE147436_series_matrix.txt"


def parse_header_field(lines, field_name):
    for line in lines:
        if line.startswith(f"!{field_name}\t"):
            values = line.rstrip("\n").split("\t")[1:]
            return [v.strip('"') for v in values]
    return None


def main():
    with open(SERIES_MATRIX, encoding="utf-8", errors="replace") as f:
        header_lines = []
        for line in f:
            if line.startswith("!series_matrix_table_begin"):
                break
            header_lines.append(line)

    gsm_ids = parse_header_field(header_lines, "Sample_geo_accession")
    titles = parse_header_field(header_lines, "Sample_title")
    source_name = parse_header_field(header_lines, "Sample_source_name_ch1")
    description = parse_header_field(header_lines, "Sample_description")  # sentrix barcode_position

    # There are 3 repeated !Sample_characteristics_ch1 lines: cell type, osk, timepoint
    char_lines = [l for l in header_lines if l.startswith("!Sample_characteristics_ch1\t")]
    cell_type = [v.strip('"').replace("cell type: ", "") for v in char_lines[0].rstrip("\n").split("\t")[1:]]
    osk = [v.strip('"').replace("osk: ", "") for v in char_lines[1].rstrip("\n").split("\t")[1:]]
    timepoint = [v.strip('"').replace("status/time point: ", "") for v in char_lines[2].rstrip("\n").split("\t")[1:]]

    sentrix_id = [d.split("_")[0] for d in description]
    sentrix_position = [d.split("_")[1] for d in description]

    df = pd.DataFrame({
        "GSM_ID": gsm_ids,
        "Sample_Name": titles,
        "Sentrix_ID": sentrix_id,
        "Sentrix_Position": sentrix_position,
        "cell_type": cell_type,
        "osk_treatment": osk,
        "timepoint": timepoint,
        "source_name": source_name,
    })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "sample_sheet.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path} ({len(df)} samples)")
    print(df.to_string(index=False))

    # Cross-check against files actually on disk
    idat_dir = RAW_DIR / "idat"
    on_disk = sorted(idat_dir.glob("*.idat.gz"))
    print(f"\n{len(on_disk)} IDAT files found on disk ({len(on_disk)//2} sample pairs expected: {len(df)})")

    missing = []
    for gsm in df["GSM_ID"]:
        matches = list(idat_dir.glob(f"{gsm}_*_Grn.idat.gz"))
        if not matches:
            missing.append(gsm)
    if missing:
        print(f"WARNING: no IDAT files found for: {missing}")
    else:
        print("All GSM IDs in sample sheet have matching IDAT files on disk.")


if __name__ == "__main__":
    main()
