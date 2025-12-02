# DLCDatabaseSetup

A reusable pipeline for ingesting DeepLabCut (DLC) pose-estimation data into a PostgreSQL database.

## Overview

This repository provides a modular workflow to:
1. Process DLC output CSV files
2. Extract metadata from video filenames
3. Normalize body part coordinates
4. Store pose data and metadata in a PostgreSQL database

The pipeline is designed to be experiment-agnostic and can be adapted for any DLC project.

## Repository Structure

```
DLCDatabaseSetup/
├── notebooks/                      # Jupyter notebooks for database setup
│   ├── 10_DLCjupyter.ipynb        # DLC project setup
│   ├── 20_set_up_deeplabcut_db.ipynb  # Database initialization
│   ├── 21_insert_features_to_db.ipynb # Data ingestion (method 1)
│   ├── 22_normalizedCSVs.ipynb    # Coordinate normalization
│   └── 23_insert_features_to_db.ipynb # Data ingestion (method 2)
├── scripts/                        # Python utility modules
│   ├── Extract_db_columns/        # Metadata extraction functions
│   ├── Insert_to_featuretable/    # Database insertion utilities
│   └── config.py                  # Database connection configuration
├── data/                           # Input CSV files (not tracked)
├── environment.yml                 # Conda environment specification
└── requirements.txt                # Pip package list

```

## Setup

### 1. Environment Setup

```bash
# Create conda environment
conda env create -f environment.yml
conda activate DLC

# Or install with pip
pip install -r requirements.txt
```

### 2. Database Configuration

Edit `scripts/config.py` to configure your PostgreSQL connection:

```python
def get_conn():
    return psycopg2.connect(
        dbname="your_database_name",
        user="your_username",
        password="your_password",
        host="your_host",
        port="5432"
    )
```

### 3. Data Preparation

Place your DLC output CSV files in the `data/` directory. The expected format is documented in `data/DATA_README.md`.

## Workflow

1. **Initialize Database** (`20_set_up_deeplabcut_db.ipynb`)
   - Creates `dlc_table` and related schemas
   - Defines columns: id, video_name, task, modulation, etc.

2. **Normalize Coordinates** (`22_normalizedCSVs.ipynb`)
   - Converts pixel coordinates to normalized arena coordinates
   - Applies coordinate transformations based on arena boundaries

3. **Insert Data** (`21_insert_features_to_db.ipynb` or `23_insert_features_to_db.ipynb`)
   - Ingests DLC CSV files into PostgreSQL
   - Extracts metadata from video filenames
   - Validates likelihood thresholds

## Output

The pipeline produces a PostgreSQL database with the following structure:

- **dlc_table**: Metadata for each trial (id, task, modulation, video_path, etc.)
- **pose tables**: Coordinate data for each body part (x, y, likelihood per frame)

## Dependencies

- Python 3.8+
- DeepLabCut 2.3.9
- PostgreSQL
- Key packages: pandas, numpy, psycopg2, scipy

See `requirements.txt` for full list.

## Integration with Analysis Pipelines

This repository provides the database foundation. For ghrelin-specific behavioral analysis, see:
- [GhrelinBehaviorQuantification](https://github.com/atanugiri/GhrelinBehaviorQuantification)

## Citation

If you use this pipeline, please cite:
- DeepLabCut: Mathis et al. (2018) Nature Neuroscience
- This repository: [Add Zenodo DOI when available]

## License

[Specify your license]

## Contact

For questions or issues, please open a GitHub issue or contact [your email].
