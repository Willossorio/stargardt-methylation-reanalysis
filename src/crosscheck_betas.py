"""
Sanity check: correlate our independently-computed beta values (from raw
IDATs via methylprep) against the authors' own processed beta matrix (from
the GEO series matrix), per sample. High per-sample correlation means our
processing pipeline reproduces the general methylation signal, even though
the exact preprocessing choices (normalization, quality masking) differ.

Run from repo root: .venv/bin/python src/crosscheck_betas.py
"""
import gzip
from pathlib import Path

import pandas as pd

OURS_PATH = Path("data/processed/beta_values_ours.csv")
SERIES_MATRIX = Path("data/raw/GSE147436_series_matrix.txt.gz")
SAMPLE_SHEET_PATH = Path("data/processed/sample_sheet.csv")


def load_authors_betas():
    with gzip.open(SERIES_MATRIX, "rt", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if line.startswith("!series_matrix_table_begin"):
                skip = i + 1
                break
    df = pd.read_csv(SERIES_MATRIX, sep="\t", skiprows=skip, skipfooter=1, engine="python", quotechar='"')
    return df.set_index("ID_REF")


def main():
    ours = pd.read_csv(OURS_PATH, index_col=0)
    theirs = load_authors_betas()

    sample_sheet = pd.read_csv(SAMPLE_SHEET_PATH, dtype={"Sentrix_ID": str})
    sample_sheet["column_id"] = sample_sheet["Sentrix_ID"] + "_" + sample_sheet["Sentrix_Position"]
    gsm_to_column = dict(zip(sample_sheet["GSM_ID"], sample_sheet["column_id"]))

    common_probes = ours.index.intersection(theirs.index)
    print(f"Comparing {len(common_probes)} probes common to both matrices")

    correlations = {}
    for gsm, column_id in gsm_to_column.items():
        if column_id not in ours.columns or gsm not in theirs.columns:
            continue
        merged = pd.DataFrame({
            "ours": ours.loc[common_probes, column_id],
            "theirs": theirs.loc[common_probes, gsm],
        }).dropna()
        correlations[gsm] = merged["ours"].corr(merged["theirs"])

    corr_series = pd.Series(correlations, name="pearson_r").sort_values()
    print(corr_series.to_string())
    print(f"\nMean correlation: {corr_series.mean():.4f}, min: {corr_series.min():.4f}")


if __name__ == "__main__":
    main()
