"""
Compare predicted epigenetic age (Horvath skin & blood clock) between
OSK-treated and control samples, at each timepoint (no damage / 1-day post
vincristine injury / 9-day recovery).

Design note: each Sentrix chip (Sentrix_ID) is one biological-replicate batch
containing both an OSK and a control arm at every timepoint, so we treat
Sentrix_ID as a pairing/blocking variable - this controls for batch effects
between chips, which is important given how few replicates there are (3
chips total). Where a chip has 2 replicate wells for the same condition and
timepoint (the "recover" groups), we average them into one value per chip
first, so every comparison below is a clean paired (n=3) test.

This is a small, exploratory analysis (n=3 biological replicates) - treat
p-values as suggestive, not confirmatory.

Run from repo root: .venv/bin/python src/compare_groups.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

AGE_PATH = Path("data/processed/epigenetic_age.csv")
RESULTS_DIR = Path("results")

TIMEPOINT_ORDER = [
    "no vincristine damage",
    "1d vincristine damage",
    "9d post vincristine damage",
]


def main():
    df = pd.read_csv(AGE_PATH, dtype={"Sentrix_ID": str})

    # Collapse the 2 replicate wells per chip/condition/timepoint (only
    # present for the "recover" groups) down to one value per chip.
    per_chip = (
        df.groupby(["Sentrix_ID", "osk_treatment", "timepoint"])["predicted_age_years"]
        .mean()
        .reset_index()
    )

    print("Per-chip (batch-averaged) predicted ages:")
    print(per_chip.to_string(index=False))

    print("\nGroup summary (mean +/- SD across the 3 chips):")
    summary = per_chip.groupby(["timepoint", "osk_treatment"])["predicted_age_years"].agg(["mean", "std", "count"])
    print(summary)

    print("\nPaired t-test (OSK vs control, paired by chip) at each timepoint:")
    results = []
    for tp in TIMEPOINT_ORDER:
        sub = per_chip[per_chip["timepoint"] == tp]
        control = sub[sub["osk_treatment"] == "no"].set_index("Sentrix_ID")["predicted_age_years"]
        osk = sub[sub["osk_treatment"] == "yes"].set_index("Sentrix_ID")["predicted_age_years"]
        chips = control.index.intersection(osk.index)
        diff = osk.loc[chips] - control.loc[chips]
        t_stat, p_val = stats.ttest_rel(osk.loc[chips], control.loc[chips])
        results.append({
            "timepoint": tp,
            "n_pairs": len(chips),
            "mean_diff_osk_minus_control": diff.mean(),
            "t_stat": t_stat,
            "p_value": p_val,
        })
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(RESULTS_DIR / "osk_vs_control_paired_ttests.csv", index=False)
    per_chip.to_csv(RESULTS_DIR / "per_chip_predicted_age.csv", index=False)

    # Plot: predicted age across timepoints, split by OSK treatment
    fig, ax = plt.subplots(figsize=(7, 5))
    for treatment, marker, color in [("no", "o", "tab:gray"), ("yes", "s", "tab:blue")]:
        sub = per_chip[per_chip["osk_treatment"] == treatment]
        means = sub.groupby("timepoint")["predicted_age_years"].mean().reindex(TIMEPOINT_ORDER)
        sds = sub.groupby("timepoint")["predicted_age_years"].std().reindex(TIMEPOINT_ORDER)
        label = "OSK" if treatment == "yes" else "Control (tTA only)"
        ax.errorbar(range(len(TIMEPOINT_ORDER)), means, yerr=sds, marker=marker, color=color, label=label, capsize=4)
    ax.set_xticks(range(len(TIMEPOINT_ORDER)))
    ax.set_xticklabels(["No damage", "1d post-VCS", "9d post-VCS\n(recovery)"])
    ax.set_ylabel("Predicted epigenetic age (Horvath skin & blood clock, years)")
    ax.set_title("Predicted epigenetic age vs. OSK treatment and injury timepoint\n(SH-SY5Y neurons, GSE147436 - independent reanalysis)")
    ax.legend()
    fig.tight_layout()
    fig_path = RESULTS_DIR / "epigenetic_age_by_condition.png"
    fig.savefig(fig_path, dpi=150)
    print(f"\nWrote {fig_path}")


if __name__ == "__main__":
    main()
