# DLCDatabaseSetup

A reusable pipeline for ingesting DeepLabCut (DLC) pose-estimation data into a csv database.

## Overview

This repository provides a modular workflow to:
1. Extract metadata from video filenames
2. Store pose data and metadata in a csv database


## Repository Structure

```
DLCDatabaseSetup/
├── notebooks/                      # Jupyter notebooks for database setup
│   ├── 10_DLCjupyter.ipynb        # Example notebook for exploration
├── scripts/                        # Python utility modules used to build the CSV/database and ingest data
│   ├── generate_dlc_table.py      # Create DLC CSV/table from raw data and metadata
│   ├── parse_video_name.py        # Extract metadata from filenames
│   ├── video_info.py              # Utilities for video metadata
│   └── config.py                  # Database connection configuration
├── data/                           # Input CSV files (not tracked)
├── environment.yml       # Conda environment specification (name: `dlc-light`)
└── requirements.txt                # Pip package list

```

## Setup

### 1. Environment Setup

This repository uses a single conda environment file:

- `environment.yml` — the conda environment for this project (name: `dlc-light`).

Create the environment and activate it (run in `zsh`):

```bash
conda env create --file environment.yml
conda activate dlc-light
```

If you prefer to install additional Python-only packages with `pip` after activating the environment:

```bash
pip install -r requirements.txt
```

### 2. Database Configuration

This project no longer uses PostgreSQL. The scripts generate and consume a CSV-backed "database" (a pandas DataFrame serialized to disk).

Edit `scripts/config.py` to configure the output CSV path or other IO options. Example minimal config:

```python
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DLCTABLE_CSV = os.path.join(DATA_DIR, 'dlc_table.csv')

def get_dlc_table_path():
   return DLCTABLE_CSV
```

Scripts will read/write `DLCTABLE_CSV` (a CSV representation of the pandas DataFrame).

### 3. Data Preparation

Place your DLC output CSV files in the `data/` directory. The expected format is documented in `data/DATA_README.md`.

## Workflow

1. **Metadata extraction utilities** (`scripts/parse_video_name.py`, `scripts/extract_genotype_and_dose.py`, `scripts/extract_maze_number.py`, `scripts/video_info.py`, `scripts/find_csv_for_video.py`, etc.)
   - These modules each extract pieces of metadata for a video:
     - `parse_video_name.py`: task, modulation, date, animal name, health
     - `extract_genotype_and_dose.py`: genotype and dose multiplier
     - `extract_maze_number.py`: maze position (using mother/raw videos mapping)
     - `video_info.py`: technical metadata (frame count, frame rate, dimensions, trial length)
     - `find_csv_for_video.py`: locates the DLC tracking CSV and returns `csv_file_path`
   - Most helper functions return metadata or paths (they do not perform aggregation).

2. **Generate / inject CSV database** (`scripts/generate_dlc_table.py`)
   - `generate_dlc_table.py` composes the metadata extracted by the helpers above and builds a consolidated table (a pandas DataFrame) with one row per trial.
   - The script assigns an `id` column, collects `csv_file_path` links, and writes the consolidated CSV (default: `data/dlc_table.csv`).
   - In short: the helper modules gather metadata; `generate_dlc_table.py` injects that metadata into the CSV-backed "database" (writes/updates `dlc_table.csv`).

3. **Additional utilities** (`scripts/split_videos_by_quadrants.py`, `scripts/center_assign.py`, etc.)
   - These scripts provide supporting functionality: video splitting helpers, center assignment rules, and other utilities used before or after generating the table.

NOTE: This repository does not include a general-purpose coordinate-normalization module. Coordinate normalization / feature extraction is handled in downstream analysis (e.g., `GhrelinBehaviorQuantification`) or can be implemented on top of the generated `dlc_table.csv`.

## Output

The primary output is a consolidated CSV `data/dlc_table.csv` (a pandas DataFrame serialized to disk) containing one row per trial with the collected metadata and links to the DLC tracking CSVs.

Typical columns include: `id`, `video_name`, `num_frames`, `frame_rate`, `trial_length`,
`video_width`, `video_height`, `genotype`, `task`, `date`, `name`, `health`, `modulation`,
`maze`, `csv_file_path`, `dose_mult`, and `center` (if assigned).

## Dependencies

- Python 3.8+
- DeepLabCut 2.3.9
- PostgreSQL
- Key packages: pandas, numpy, psycopg2, scipy

See `requirements.txt` for full list.

## Integration with Analysis Pipelines

This repository provides the database foundation. For ghrelin-specific behavioral analysis, see:
- [GhrelinBehaviorQuantification](https://github.com/atanugiri/GhrelinBehaviorQuantification)

## License


## Contact

For questions or issues, please open a GitHub issue or contact atanurkm11@gmail.com.
