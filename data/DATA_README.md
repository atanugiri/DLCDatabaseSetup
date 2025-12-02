# Data Directory

This directory is where your `dlc_table` CSV files should be placed.

## Expected Format

The database ingestion scripts expect CSV files with the following columns:
- `id`: Unique identifier for each trial
- `task`: Experimental task name
- `modulation`: Treatment/modulation applied
- `video_path`: Path to the corresponding video file

## Usage

1. Place your DLC output CSVs in this directory
2. Run the notebooks in `notebooks/` to ingest data into PostgreSQL
3. The `config.py` file in `scripts/` will read from this directory

## Note

Video files should NOT be committed to git. Only CSV metadata files should be tracked.
