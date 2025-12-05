"""
Extract genotype ('white' or 'black') and dose_mult (2 or 10) from video file path.
"""

from pathlib import Path

def extract_genotype_and_dose(video_path):
    """
    Extract genotype ('white' or 'black') and dose_mult (2 or 10) from video file path.
    
    Args:
        video_path: Path to video file (str or Path object)
    
    Returns:
        (genotype, dose_mult): Tuple of ('white' or 'black', 2 or 10 or None)
    
    Example:
        "/path/to/SplitVideos/WhiteAnimals10X/FoodOnly/video.mp4" -> ('white', 10)
        "/path/to/SplitVideos/WhiteAnimals2X/FoodOnly/video.mp4" -> ('white', 2)
        "/path/to/SplitVideos/BlackAnimals/ToyOnly/video.mp4" -> ('black', None)
    """
    path_str = str(video_path).lower()
    genotype = None
    dose_mult = None
    if 'whiteanimals' in path_str:
        genotype = 'white'
        if 'whiteanimals10x' in path_str:
            dose_mult = 10
        elif 'whiteanimals2x' in path_str:
            dose_mult = 2
    elif 'blackanimals' in path_str:
        genotype = 'black'
        # Add dose_mult logic for black animals if needed
    return genotype, dose_mult

# --- Main Test Block ----------------------------------------------------------

if __name__ == "__main__":
    import sys
    import random
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    split_dirs = [
        data_dir / "SplitVideos" / "WhiteAnimals10X",
        data_dir / "SplitVideos" / "WhiteAnimals2X",
    ]
    # Get test video: from user input or random selection
    if len(sys.argv) > 1:
        test_video_path = sys.argv[1]
        print(f"Testing user-provided path: {test_video_path}")
    else:
        all_videos = []
        for vdir in split_dirs:
            if vdir.exists():
                all_videos.extend(list(vdir.rglob("*.mp4")))
        if not all_videos:
            print("No videos found in SplitVideos directory!")
            sys.exit(1)
        test_video = random.choice(all_videos)
        test_video_path = str(test_video)
        print(f"Testing randomly selected video: {test_video.name}")
        print(f"Path: {test_video_path}")
    genotype, dose_mult = extract_genotype_and_dose(test_video_path)
    print(f"  -> Genotype: {genotype}")
    print(f"  -> Dose multiplier: {dose_mult}")