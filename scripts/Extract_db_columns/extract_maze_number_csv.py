"""
Extract maze numbers from raw video filenames and update CSV metadata.
CSV-only version (no PostgreSQL dependency).
"""

from pathlib import Path
import re
import pandas as pd


# --- Helpers -----------------------------------------------------------------

# Strip trailing variations like: _Trial1, _trial_2, _Trial-03
TRIAL_SUFFIX_RX = re.compile(r'_(?:[Tt]rial)[ _-]?\d+$')

def _strip_trial_suffix(stem: str) -> str:
    return TRIAL_SUFFIX_RX.sub('', stem)

# Optional: strip quadrant suffixes like _top_left / _bottom_right
QUAD_SUFFIX_RX = re.compile(r'_(?:top|bottom)_(?:left|right)$', flags=re.I)

def _strip_quadrant_suffix(stem: str) -> str:
    return QUAD_SUFFIX_RX.sub('', stem)

def _prefix_from_stem(stem: str) -> str:
    """
    Prefix is the first 5 tokens: Task_MM_DD_YY_HealthCode
    """
    parts = stem.split('_')
    # Expect at least: Task, MM, DD, YY, HealthCode, Animal
    if len(parts) < 6:
        return ''
    return '_'.join(parts[:5])


# --- Public API ---------------------------------------------------------------

def load_mother_videos(raw_video_dirs):
    """
    Return only mother videos that end with 4 animal tokens, with optional Trial suffix.

    Matches:
      Prefix_A1_A2_A3_A4.mp4
      Prefix_A1_A2_A3_A4_Trial2.mp4
      (Prefix is everything before the 4-animal block.)
    """
    mother_pat = re.compile(
        r'^.+_(?:[^_]+_){3}[^_]+(?:_(?:[Tt]rial)[ _-]?\d+)?\.mp4$'
    )
    all_mothers = []
    for folder in raw_video_dirs:
        folder_path = Path(folder)
        if not folder_path.exists():
            print(f"Warning: Directory not found: {folder_path}")
            continue
        for p in folder_path.rglob("*.mp4"):  # Use rglob to search recursively
            if mother_pat.match(p.name):
                all_mothers.append(p)
    return all_mothers


def build_prefix_to_animal_map(mother_videos):
    """
    Build a map: 'Task_MM_DD_YY_HealthCode' -> [A1, A2, A3, A4]
    (Where animals are taken case-sensitively from filenames.)
    """
    prefix_to_animals = {}
    for mv in mother_videos:
        base = _strip_trial_suffix(mv.stem)
        # Everything before the 4-animal block is the prefix.
        m = re.match(r'^(?P<prefix>.+?)_(?P<animals>(?:[^_]+_){3}[^_]+)$', base)
        if not m:
            continue
        prefix = m.group('prefix')
        animals = m.group('animals').split('_')
        if len(animals) == 4:
            prefix_to_animals[prefix] = animals
    return prefix_to_animals


def get_maze_number(split_video_name, prefix_to_animals):
    """
    Given a split video name, extract the animal name from the filename,
    find the matching mother video, and return the maze position (1-4).
    
    Args:
        split_video_name: Filename like "FoodOnly_7_30_25_S1P_Carrot.mp4"
        prefix_to_animals: Dict mapping "Task_MM_DD_YY_HealthCode" → [Animal1, Animal2, Animal3, Animal4]
    
    Returns:
        Maze number (1-4) based on animal position in mother video, or None if not found
    
    Example:
        Mother video: FoodOnly_7_30_25_S1P_Carrot_Cauliflower_Kale_None.mp4
        Split video:  FoodOnly_7_30_25_S1P_Cauliflower.mp4
        → Returns 2 (Cauliflower is 2nd in [Carrot, Cauliflower, Kale, None])
    """
    stem = Path(split_video_name).stem
    stem = _strip_trial_suffix(stem)
    stem = _strip_quadrant_suffix(stem)

    # Extract prefix (first 5 tokens: Task_MM_DD_YY_HealthCode)
    prefix = _prefix_from_stem(stem)
    if not prefix:
        return None

    # Extract animal name (6th token)
    parts = stem.split('_')
    if len(parts) < 6:
        return None
    animal_from_filename = parts[5]
    
    # Normalize to lowercase for case-insensitive matching
    animal_clean = animal_from_filename.lower()

    # Look up the mother video's animal list
    animals = prefix_to_animals.get(prefix)
    if not animals:
        return None

    # Find which position (1-4) the animal occupies
    for i, a in enumerate(animals):
        if a.lower() == animal_clean:
            return i + 1

    return None


def update_maze_numbers_csv(csv_path, prefix_to_animals, output_csv=None):
    """
    Read CSV with video_name column, compute maze_number from the filename,
    and save to output CSV. If output_csv is None, overwrites input.
    
    Prints a clear sanity line for each update.
    
    Returns: Updated DataFrame
    """
    # Read the CSV
    df = pd.read_csv(csv_path)
    
    # Check required columns
    if 'video_name' not in df.columns:
        raise ValueError("CSV must have 'video_name' column")
    
    # Add maze column if it doesn't exist
    if 'maze' not in df.columns:
        df['maze'] = None
    
    # Update maze numbers
    for idx, row in df.iterrows():
        video_name = row['video_name']
        
        maze_number = get_maze_number(video_name, prefix_to_animals)
        
        if maze_number is not None:
            df.at[idx, 'maze'] = int(maze_number)
            
            # Print sanity check
            stem_clean = _strip_quadrant_suffix(_strip_trial_suffix(Path(video_name).stem))
            prefix = _prefix_from_stem(stem_clean)
            animals = prefix_to_animals.get(prefix, [])
            if animals:
                mother_video = f"{prefix}_{'_'.join(animals)}.mp4"
            else:
                mother_video = "(mother not found in map)"
            
            print(f"[✓] {video_name} → {mother_video} → maze {maze_number}")
        else:
            print(f"[✗] {video_name} → maze number not found")
    
    # Save output
    output_path = output_csv if output_csv else csv_path
    df.to_csv(output_path, index=False)
    print(f"\n✅ Maze number update complete. Saved to: {output_path}")
    
    return df


# --- Main Test Block ----------------------------------------------------------

if __name__ == "__main__":
    import sys
    import random
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    raw_video_dirs = [
        data_dir / "RawVideos" / "WhiteAnimals10X",
        data_dir / "RawVideos" / "WhiteAnimals2X",
    ]
    
    # Load mother videos and build mapping
    mother_videos = load_mother_videos(raw_video_dirs)
    prefix_to_animals = build_prefix_to_animal_map(mother_videos)
    print(f"Loaded {len(mother_videos)} mother videos → {len(prefix_to_animals)} prefix mappings\n")
    
    # Get test video: from user input or random selection
    if len(sys.argv) > 1:
        test_video_name = sys.argv[1]
        print(f"Testing user-provided video: {test_video_name}")
    else:
        all_splits = list((data_dir / "SplitVideos").rglob("*.mp4"))
        test_video = random.choice(all_splits)
        test_video_name = test_video.name
        print(f"Testing randomly selected video: {test_video_name}")
    
    # Get maze number
    maze_num = get_maze_number(test_video_name, prefix_to_animals)
    
    if maze_num:
        stem = _strip_trial_suffix(_strip_quadrant_suffix(Path(test_video_name).stem))
        prefix = _prefix_from_stem(stem)
        animals = prefix_to_animals.get(prefix, [])
        mother_name = f"{prefix}_{'_'.join(animals)}.mp4"
        print(f"  → Mother video: {mother_name}")
        print(f"  → Maze position: {maze_num}")
    else:
        print(f"  → Maze number not found!")
