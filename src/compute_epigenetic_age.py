"""
Apply the Horvath 2018 "skin & blood" epigenetic clock (391 CpGs + intercept,
from docs/clock_reference/horvath_skin_blood_clock_coefficients.csv, sourced
from the isglobal-brge/methylclock R package's bundled coefSkin.rda, which
mirrors the paper's Supplementary Dataset 2) to our own beta value matrix.

Method (matches methylclock's R implementation):
  1. linear_predictor = intercept + sum(beta_i * weight_i) over matched CpGs
  2. age = 21*exp(linear_predictor) - 1        if linear_predictor < 0
         = 21*linear_predictor + 20            otherwise
     (this is Horvath's standard "anti-transformation", adult.age=20)

Run from repo root: .venv/bin/python src/compute_epigenetic_age.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

BETAS_PATH = Path("data/processed/beta_values_ours.csv")
COEF_PATH = Path("docs/clock_reference/horvath_skin_blood_clock_coefficients.csv")
SAMPLE_SHEET_PATH = Path("data/processed/sample_sheet.csv")
OUT_PATH = Path("data/processed/epigenetic_age.csv")

ADULT_AGE = 20


def anti_trafo(x, adult_age=ADULT_AGE):
    x = np.asarray(x, dtype=float)
    return np.where(x < 0, (1 + adult_age) * np.expm1(x), (1 + adult_age) * x + adult_age)


def main():
    betas = pd.read_csv(BETAS_PATH, index_col=0)  # rows = CpGs, columns = samples
    coefs = pd.read_csv(COEF_PATH)

    intercept = coefs.loc[coefs["CpGmarker"] == "(Intercept)", "CoefficientTraining"].iloc[0]
    weights = coefs[coefs["CpGmarker"] != "(Intercept)"].set_index("CpGmarker")["CoefficientTraining"]

    matched = weights.index.intersection(betas.index)
    coverage = len(matched) / len(weights)
    print(f"Matched {len(matched)}/{len(weights)} clock CpGs ({coverage:.1%} coverage)")
    if coverage < 0.8:
        raise RuntimeError("Fewer than 80% of clock CpGs found in beta matrix - clock would be unreliable.")

    clock_betas = betas.loc[matched]

    # A handful of clock CpGs can be quality-masked (NaN) in every sample -
    # there's no valid per-CpG mean to impute those with, so drop them from
    # the linear predictor entirely rather than propagate NaN into every
    # sample's score. Coverage is checked again afterwards to confirm this
    # doesn't push us below a usable fraction of the clock.
    always_missing = clock_betas.index[clock_betas.isna().all(axis=1)]
    if len(always_missing) > 0:
        print(f"Dropping {len(always_missing)} clock CpGs missing in every sample: {list(always_missing)}")
        clock_betas = clock_betas.drop(index=always_missing)
        remaining_coverage = len(clock_betas) / len(weights)
        print(f"Remaining clock coverage: {len(clock_betas)}/{len(weights)} ({remaining_coverage:.1%})")
        if remaining_coverage < 0.8:
            raise RuntimeError("Coverage dropped below 80% after removing always-missing CpGs.")

    n_missing_per_sample = clock_betas.isna().sum()
    if n_missing_per_sample.sum() > 0:
        print("Missing (NaN, quality-masked) values per sample among remaining clock CpGs:")
        print(n_missing_per_sample[n_missing_per_sample > 0])
    # Standard practice for these clocks: impute any remaining sample-specific
    # missing CpG with that CpG's mean across the other samples in this dataset.
    clock_betas = clock_betas.apply(lambda row: row.fillna(row.mean()), axis=1)

    linear_predictor = clock_betas.T.dot(weights.loc[clock_betas.index]) + intercept
    predicted_age = pd.Series(anti_trafo(linear_predictor.values), index=linear_predictor.index, name="predicted_age_years")

    sample_sheet = pd.read_csv(SAMPLE_SHEET_PATH, dtype={"Sentrix_ID": str})
    # beta matrix columns are Sentrix_ID_Sentrix_Position; sample sheet has these as separate columns
    sample_sheet["column_id"] = sample_sheet["Sentrix_ID"] + "_" + sample_sheet["Sentrix_Position"]

    result = sample_sheet.set_index("column_id").join(predicted_age)
    result = result.reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {OUT_PATH}")
    print(result[["GSM_ID", "Sample_Name", "osk_treatment", "timepoint", "predicted_age_years"]].to_string(index=False))


if __name__ == "__main__":
    main()
