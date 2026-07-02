# Data notes: GSE147436

## Source

- GEO Series: [GSE147436](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE147436)
- Title: "Reprogramming to recover youthful epigenetic information and restore vision" (methylation sub-study)
- Platform: Illumina Infinium HumanMethylation EPIC (850K) BeadChip, GPL23976
- Associated publication: PMID 33268865 (Lu et al., 2020, Nature)
- Contributors listed on the series: Steve Horvath, Xiao Tian, Yuancheng Lu, David Sinclair

## What's actually in this dataset

This GEO series contains **only the in-vitro cell-culture methylation arm** of the
broader reprogramming study. It profiles differentiated SH-SY5Y (human
neuroblastoma-derived neuron-like) cells, **not** the retinal ganglion cells or
optic nerve tissue used in the mouse vision-restoration experiments reported in
the same paper. There is no vision, RGC, or optic nerve data of any kind in
GSE147436 — see the disclaimer in [README.md](../README.md).

## Design (24 samples)

3 biological replicates x 2 arms x 4 conditions, though conditions are really
2 factors (`osk_treatment` x `timepoint`) - see
`data/processed/sample_sheet.csv` (built by `src/build_sample_sheet.py`):

- **osk_treatment**: `no` (tTA control vector only) vs `yes` (AAV.DJ-delivered
  Oct4/Sox2/Klf4)
- **timepoint** / `source_name`:
  - `tTA` / `OSK+tTA` - no vincristine (VCS) damage (baseline)
  - `tTA_VCS` / `OSK+tTA_VCS` - 1 day after vincristine-induced axonal injury
  - `tTA_VCS_recover` / `OSK+tTA_VCS_recover` - 9 days post-injury (recovery
    window), with 2 replicates per Sentrix chip per condition here, giving 6
    replicates total for the recovery groups

Samples are spread across 3 Sentrix chips (`203440280002`, `203440280011`,
`203440280018`), 8 positions each (R01C01-R08C01), which matches one full
BeadChip per biological replicate batch.

## Files

| File | What it is |
|---|---|
| `data/raw/GSE147436_RAW.tar` | Original download from GEO (338 MB) |
| `data/raw/idat/*.idat.gz` | 48 raw IDAT files = 24 samples x {Grn, Red} channel, unprocessed intensities straight off the scanner |
| `data/raw/GSE147436_series_matrix.txt.gz` | GEO series matrix; header has full sample metadata, and the embedded table is the **authors' own normalized beta-value matrix** (865,859 probes x 24 samples, values in [0,1], no missing data) |
| `data/processed/sample_sheet.csv` | Sample sheet we derived from the series matrix header, methylprep-sheet-compatible (GSM_ID, Sentrix_ID, Sentrix_Position, osk_treatment, timepoint, etc.) |

## Verification performed

- Confirmed the tar contains exactly 48 gzipped IDAT files (24 pairs).
- Parsed one IDAT file with `methylprep` and confirmed it identifies as an
  EPIC "BeadChip 8x5" with ~1.05M probe addresses - consistent with the stated
  platform.
- Cross-checked every GSM ID in the sample sheet against the IDAT filenames on
  disk - all 24 present, no orphans or gaps.
- Loaded the authors' processed beta matrix and confirmed shape, [0,1] value
  bounds, and zero missing values.

## Two possible reanalysis paths

1. **Reprocess from raw IDATs** with `methylprep` (background correction,
   dye-bias correction, normalization) - more independent/rigorous, lets us
   make our own preprocessing choices and QC decisions explicit.
2. **Use the authors' processed beta matrix** from the series matrix as a
   quick sanity check / starting point, while being transparent that those
   values were not computed by us.

Recommended: do (1) as the primary pipeline, and use (2) only as a
cross-check that our independent processing reproduces the general pattern
of the authors' results.
