# Results summary: independent reanalysis of GSE147436

## Disclaimer (repeated from README - important context)

This analyzes the OSK-treated SH-SY5Y neuron methylation sub-study only
(GSE147436), not the mouse vision-restoration experiments from the same
paper (Lu et al., 2020, *Nature*). See [README.md](../README.md) and
[data_notes.md](data_notes.md).

## Pipeline

1. Downloaded raw IDAT files (24 samples, Illumina EPIC array) and processed
   them independently with `methylprep` (background correction, dye-bias
   correction, quality masking) - see [src/run_pipeline.py](../src/run_pipeline.py).
2. Cross-checked our beta values against the authors' processed matrix from
   the GEO series matrix: per-sample Pearson correlation ranged 0.9967-0.9972
   (mean 0.9972) - see [src/crosscheck_betas.py](../src/crosscheck_betas.py).
   Our independent pipeline reproduces the same underlying signal; small
   differences reflect different preprocessing/normalization choices.
3. Applied the Horvath 2018 "skin & blood" epigenetic clock (391 CpGs,
   coefficients from the `methylclock` R package's bundled data, which
   mirrors the paper's supplementary table) to our beta values - see
   [src/compute_epigenetic_age.py](../src/compute_epigenetic_age.py).
   374/391 clock CpGs (95.7%) were usable; 17 were quality-masked in every
   sample and excluded.
4. Compared predicted epigenetic age between OSK-treated and control samples
   at each timepoint, pairing by Sentrix chip (batch) to control for
   batch effects - see [src/compare_groups.py](../src/compare_groups.py).

## Key caveat: absolute ages are not meaningful here

SH-SY5Y is an immortalized neuroblastoma-derived cell line, not normal human
tissue, and its genome-wide methylation pattern is highly abnormal compared
to what the Horvath clock was trained on. This produces predicted ages far
outside any plausible chronological range (all samples: -19.6 to -19.9
"years"). This is expected and is not a bug - only *relative* differences
between conditions are potentially interpretable, which is consistent with
how the original paper used this method.

## Findings

| Timepoint | n pairs | Mean difference (OSK - control) | t | p |
|---|---|---|---|---|
| No damage (baseline) | 3 | +0.129 | 2.01 | 0.182 |
| 1 day post-vincristine | 3 | -0.043 | -1.05 | 0.403 |
| 9 days post-vincristine (recovery) | 3 | +0.031 | 1.80 | 0.214 |

(Full numbers in [results/osk_vs_control_paired_ttests.csv](../results/osk_vs_control_paired_ttests.csv)
and [results/per_chip_predicted_age.csv](../results/per_chip_predicted_age.csv).)

**No comparison reached statistical significance**, and the direction of the
small OSK-vs-control difference is not even consistent across timepoints
(positive, then negative, then positive again). See
[results/epigenetic_age_by_condition.png](../results/epigenetic_age_by_condition.png).

## Interpretation

With this specific clock and this specific independent preprocessing
pipeline, we do not find a clear, directionally consistent, or statistically
significant shift in Horvath skin & blood clock-predicted age attributable
to OSK expression in this dataset. Important caveats before drawing any
conclusion from this:

- **n = 3 biological replicates per condition** is very underpowered for
  detecting a subtle effect - a true effect could easily be missed here.
- We used one specific epigenetic clock (Horvath skin & blood, 2018). The
  original study may have emphasized different metrics or a different
  clock/statistical approach; a null result with this clock does not
  contradict findings obtained by other methods.
- This cell line's abnormal methylome (see caveat above) is a genuinely
  difficult substrate for any clock trained on normal tissue, which adds
  noise beyond ordinary biological/technical variability.
- This is one independent reanalysis with our own preprocessing choices;
  it is not a formal replication attempt of the original paper's statistics.

This result should be read as: *an independent pipeline applied to the
publicly available raw data does not, on its own, reproduce a clear
epigenetic-age-reversal signal using this specific clock* - not as a
refutation of the original paper's conclusions, which likely rest on
additional evidence and different analytical choices.
