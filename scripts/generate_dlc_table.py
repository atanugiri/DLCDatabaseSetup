"""
Generate dlc_table.csv from split videos by extracting metadata.

Combines all utility modules to create a comprehensive metadata CSV:
- parse_video_name: task, modulation, date, animal name, health
- extract_maze_number: maze position
- video_info: frames, fps, dimensions, trial_length
- find_csv_for_video: DLC CSV file path
- determine_genotype: white/black classification
"""

from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Import utility functions
from parse_video_name import parse_video_name
from extract_maze_number import load_mother_videos, build_prefix_to_animal_map, get_maze_number
from video_info import get_video_info
from find_csv_for_video import find_csv_for_video
from determine_genotype import determine_genotype


def generate_dlc_table(output_path=None):
    """
    Generate dlc_table.csv from WhiteAnimals split videos only.
    
    Args:
        output_path: Path to save CSV. If None, saves to data/dlc_table.csv
    """
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    if output_path is None:
        output_path = data_dir / "dlc_table.csv"
    
    # Directories for split videos (WhiteAnimals only)
    split_video_dirs = [
        data_dir / "SplitVideos" / "WhiteAnimals10X",
        data_dir / "SplitVideos" / "WhiteAnimals2X",
    ]
    
    # Directories for DLC CSVs (WhiteAnimals only)
    csv_dirs = [
        data_dir / "DlcDataPytorchFiltered" / "WhiteAnimals10X",
        data_dir / "DlcDataPytorchFiltered" / "WhiteAnimals2X",
    ]
    
    # Directories for raw videos (for maze number extraction, WhiteAnimals only)
    raw_video_dirs = [
        data_dir / "RawVideos" / "WhiteAnimals10X",
        data_dir / "RawVideos" / "WhiteAnimals2X",
    ]
    
    print("Loading mother videos for maze number extraction...")
    mother_videos = load_mother_videos(raw_video_dirs)
    prefix_to_animals = build_prefix_to_animal_map(mother_videos)
    print(f"Loaded {len(mother_videos)} mother videos → {len(prefix_to_animals)} prefix mappings\n")
    
    # Collect all split videos
    print("Collecting split videos...")
    all_videos = []
    for vdir in split_video_dirs:
        if vdir.exists():
            all_videos.extend(list(vdir.rglob("*.mp4")))
    
    print(f"Found {len(all_videos)} split videos\n")
    
    # Process each video
    records = []
    print("Processing videos...")
    
    for video_path in tqdm(all_videos, desc="Extracting metadata"):
        video_name = video_path.name
        
        # Parse video name
        task, modulation, date, name, health = parse_video_name(video_name)
        
        if not task:
            print(f"\n[WARNING] Failed to parse: {video_name}")
            continue
        
        # Get maze number
        maze = get_maze_number(video_name, prefix_to_animals)
        
        # Get video info
        num_frames, frame_rate, width, height, trial_length = get_video_info(str(video_path))
        
        # Find DLC CSV file
        csv_file_path = find_csv_for_video(video_name, csv_dirs)
        
        # Determine genotype
        genotype = determine_genotype(video_path)
        
        # Create record
        record = {
            'video_name': video_name,
            'num_frames': num_frames,
            'frame_rate': frame_rate,
            'trial_length': trial_length,
            'video_width': width,
            'video_height': height,
            'genotype': genotype,
            'task': task,
            'date': date,
            'name': name,
            'health': health,
            'modulation': modulation,
            'maze': maze,
            'csv_file_path': csv_file_path,
            'dose_mult': None,  # To be filled in later if needed
            'center': None,     # To be filled in later if needed
        }
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Add ID column
    df.insert(0, 'id', range(1, len(df) + 1))
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\n✅ Successfully generated dlc_table.csv with {len(df)} records")
    print(f"   Saved to: {output_path}")
    
    # Print summary statistics
    print(f"\n📊 Summary:")
    print(f"   Total videos: {len(df)}")
    if 'genotype' in df.columns and df['genotype'].notna().any():
        print(f"   Genotypes: {df['genotype'].value_counts().to_dict()}")
    print(f"   Tasks: {df['task'].value_counts().to_dict()}")
    print(f"   Health: {df['health'].value_counts().to_dict()}")
    print(f"   Videos with CSV: {df['csv_file_path'].notna().sum()}")
    print(f"   Videos with maze: {df['maze'].notna().sum()}")
    
    return df


# --- Main Test Block ----------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    # Allow optional output path from command line
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=" * 70)
    print("Generating dlc_table.csv")
    print("=" * 70 + "\n")
    
    df = generate_dlc_table(output_path)
    
    print("\n" + "=" * 70)
    print("Generation complete!")
    print("=" * 70)
