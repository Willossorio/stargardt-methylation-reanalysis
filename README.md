# Stargardt / OSK Reprogramming Methylation Reanalysis

**See [WRITEUP.md](WRITEUP.md) for the full writeup of methods and results.**

## Disclaimer

**This is an independent reanalysis of a publicly deposited dataset, not a
reproduction of the original vision-restoration mouse study.**

The original paper (Lu et al., 2020, *Nature*, PMID 33268865) reported that
partial epigenetic reprogramming with Oct4/Sox2/Klf4 (OSK) could restore
vision in a mouse model of optic nerve damage and glaucoma, and separately
profiled DNA methylation in an OSK-treated human neuronal cell line
(SH-SY5Y) as a mechanistic side experiment. The GEO dataset analyzed in this
repository, [GSE147436](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE147436),
is **only** that cell-culture methylation sub-study. It contains no retinal
ganglion cell, optic nerve, or in-vivo mouse data. Any conclusions drawn here
apply to methylation dynamics in a human neuroblastoma-derived cell line
after OSK expression and chemical axonal injury - they say nothing directly
about vision restoration.

## What this project does

Independently reprocesses and reanalyzes the raw Illumina EPIC methylation
array data (IDAT files) from GSE147436 to examine whether OSK expression
shifts epigenetic-clock-based biological age estimates in damaged vs.
recovering neurons, using our own preprocessing pipeline rather than relying
solely on the authors' processed values.

See [docs/data_notes.md](docs/data_notes.md) for a full description of what's
in the dataset and how we verified it.

## Repo structure

```
data/
  raw/            # Original downloads from GEO (gitignored - see Setup)
    idat/         # Extracted raw IDAT files
  processed/      # Derived files we generate (sample sheet, beta matrices, age estimates)
notebooks/        # Exploratory analysis notebooks
src/              # Reusable scripts (data prep, QC, epigenetic clock, plotting)
results/          # Figures and tables for the writeup
docs/             # Data notes, methods, writeup drafts
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Data is not committed to git (see `.gitignore`) since it's large and
re-downloadable. To fetch it again:

```bash
curl -o data/raw/GSE147436_RAW.tar \
  "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE147436&format=file"
tar -xf data/raw/GSE147436_RAW.tar -C data/raw/idat

curl -o data/raw/GSE147436_series_matrix.txt.gz \
  "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE147nnn/GSE147436/matrix/GSE147436_series_matrix.txt.gz"

python src/build_sample_sheet.py
```

## Status

- [x] Project scaffold + git repo
- [x] Python environment + requirements
- [x] Raw data downloaded and verified (24 samples, EPIC array, IDATs + processed beta matrix)
- [x] Sample sheet built and cross-checked against files on disk
- [x] IDAT preprocessing pipeline (background/dye-bias correction, normalization) via `methylprep`
- [x] Epigenetic age estimation (Horvath skin & blood clock)
- [x] Statistical comparison across OSK / timepoint groups
- [ ] Writeup

See [docs/results_summary.md](docs/results_summary.md) for findings so far.

### A note on the Python environment

`methylprep` (last released 2023) depends on pandas/numpy APIs that were
removed in newer releases, and no compatible old version of those libraries
has a prebuilt wheel for very new Pythons. This project therefore pins its
virtual environment to **Python 3.11** (installed via
[`uv`](https://docs.astral.sh/uv/), which manages this independently of
your system Python) rather than whatever Python you may have installed
system-wide:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.11
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```
