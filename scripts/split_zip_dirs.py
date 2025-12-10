#!/usr/bin/env python3
"""
Zip each top-level folder under the `data/` directory and split the resulting .zip
into multiple parts not exceeding a configurable maximum size.

Parts are named like `<FolderName>.zip.part001`, `<FolderName>.zip.part002`, ...
To reconstruct and extract:

  cat FolderName.zip.part* > FolderName.zip
  unzip FolderName.zip

Usage:
  python scripts/split_zip_dirs.py --data-dir data --max-gb 2.5

Notes:
- This script first creates a single zip file for each folder (uses disk space equal to
  the resulting un-split zip). It then splits that zip into parts and deletes the
  original zip to reclaim space.
- Ensure you have enough disk space before running on large folders.
"""

from pathlib import Path
import argparse
import shutil
import os
import math
import sys

DEFAULT_MAX_GB = 2.3


def split_file(input_path: Path, max_bytes: int):
    """Split `input_path` into sequential part files of up to `max_bytes` bytes.

    The generated part files will be named `input_path` + `.partNNN` (001-based,
    zero-padded to 3 digits). Concatenating those parts in order will recreate the
    original zip file.
    """
    size = input_path.stat().st_size
    if size <= max_bytes:
        print(f"No splitting needed for {input_path.name} ({size} bytes)")
        return [input_path]

    parts = []
    with input_path.open('rb') as f:
        idx = 1
        while True:
            chunk = f.read(max_bytes)
            if not chunk:
                break
            part_name = input_path.with_name(f"{input_path.name}.part{idx:03d}")
            with part_name.open('wb') as pf:
                pf.write(chunk)
            parts.append(part_name)
            print(f"Wrote {part_name.name} ({len(chunk)} bytes)")
            idx += 1

    return parts


def zip_folder(folder: Path, output_zip: Path):
    """Create a zip archive of `folder` at `output_zip`.

    Returns the path to the created zip file.
    """
    # shutil.make_archive takes base_name without extension
    base_name = str(output_zip.with_suffix(''))
    root_dir = str(folder)
    print(f"Creating zip for {folder} → {base_name}.zip")
    archive = shutil.make_archive(base_name, 'zip', root_dir=root_dir)
    return Path(archive)


def process_data_dir(data_dir: Path, max_bytes: int, remove_zip_after_split: bool = True):
    """Find top-level directories in `data_dir`, zip each, split into parts.

    Returns a dict mapping folder name -> list of generated part paths.
    """
    results = {}
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # iterate over top-level directories in data_dir
    for child in sorted(data_dir.iterdir()):
        if not child.is_dir():
            continue

        folder_name = child.name
        out_zip = data_dir / f"{folder_name}.zip"

        # create zip
        try:
            zip_path = zip_folder(child, out_zip)
        except Exception as e:
            print(f"Failed to create zip for {child}: {e}")
            continue

        # split zip into parts
        try:
            parts = split_file(zip_path, max_bytes)
        except Exception as e:
            print(f"Failed to split {zip_path}: {e}")
            continue

        # optionally remove original zip if splitting was done
        if remove_zip_after_split and len(parts) > 1:
            try:
                zip_path.unlink()
                print(f"Removed temporary zip: {zip_path.name}")
            except Exception as e:
                print(f"Warning: failed to remove {zip_path}: {e}")

        results[folder_name] = parts

    return results


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Create per-folder zips and split into parts")
    p.add_argument('--data-dir', default='data', help='Path to the data directory (default: data)')
    p.add_argument('--max-gb', type=float, default=DEFAULT_MAX_GB,
                   help=f'Maximum size of each part in GB (default: {DEFAULT_MAX_GB})')
    p.add_argument('--no-remove-original', dest='remove_original', action='store_false',
                   help='Do not remove the original combined zip after splitting')
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    # Resolve data_dir relative to the project root when a relative path is provided.
    # This allows calling the script either from the repository root:
    #   python scripts/split_zip_dirs.py --data-dir data
    # or from the `scripts/` directory directly:
    #   cd scripts && python split_zip_dirs.py --data-dir data
    data_dir = Path(args.data_dir)
    if not data_dir.is_absolute():
        # project root is one level up from this script's directory
        project_root = Path(__file__).parent.parent.resolve()
        data_dir = (project_root / data_dir).resolve()

    max_bytes = int(args.max_gb * (1024 ** 3))

    print(f"Data dir: {data_dir}")
    print(f"Max part size: {args.max_gb} GB ({max_bytes} bytes)")

    res = process_data_dir(data_dir, max_bytes, remove_zip_after_split=args.remove_original)

    print('\nSummary:')
    for k, parts in res.items():
        print(f"- {k}: {len(parts)} part(s)")

    print('\nDone.')


if __name__ == '__main__':
    main()
