"""
Find DLC CSV file corresponding to a video filename.
Searches recursively in the DlcDataPytorchFiltered directory.
"""

from pathlib import Path


def find_csv_for_video(video_name, csv_dirs):
    """
    Given a video filename, search for the corresponding DLC CSV recursively.

    Args:
        video_name: Name of the video file (e.g., "FoodOnly_7_30_25_S1P_Carrot.mp4")
        csv_dirs: List of directories to search for CSV files

    Returns:
        Full path to the matched CSV file, or None if no match is found
        
    Example:
        Video: "FoodOnly_7_30_25_S1P_Carrot.mp4"
        Finds: "FoodOnly_7_30_25_S1P_CarrotDLC_resnet50_AnimalBehaviorJun6shuffle1_1030000_filtered.csv"
    """
    stem = Path(video_name).stem  # Remove file extension
    pattern = f"{stem}DLC*_filtered.csv"  # Pattern to match DLC CSV files
    
    for csv_dir in csv_dirs:
        csv_path = Path(csv_dir)
        if not csv_path.exists():
            continue
        
        # Search recursively for matching CSV
        matches = list(csv_path.rglob(pattern))
        if matches:
            return str(matches[0])
    
    return None


# --- Main Test Block ----------------------------------------------------------

if __name__ == "__main__":
    import sys
    import random
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    csv_dirs = [
        data_dir / "DlcDataPytorchFiltered" / "WhiteAnimals10X",
        data_dir / "DlcDataPytorchFiltered" / "WhiteAnimals2X",
    ]
    
    # Get test video: from user input or random selection
    if len(sys.argv) > 1:
        test_video_name = sys.argv[1]
        print(f"Testing user-provided video: {test_video_name}")
    else:
        # Find a random split video
        split_dirs = [
            data_dir / "SplitVideos" / "WhiteAnimals10X",
            data_dir / "SplitVideos" / "WhiteAnimals2X",
        ]
        all_videos = []
        for vdir in split_dirs:
            all_videos.extend(list(Path(vdir).rglob("*.mp4")))
        
        if not all_videos:
            print("No videos found in SplitVideos directory!")
            sys.exit(1)
        
        test_video = random.choice(all_videos)
        test_video_name = test_video.name
        print(f"Testing randomly selected video: {test_video_name}")
    
    # Find matching CSV
    csv_path = find_csv_for_video(test_video_name, csv_dirs)
    
    if csv_path:
        print(f"  → Found CSV: {csv_path}")
    else:
        print(f"  → No matching CSV found!")
