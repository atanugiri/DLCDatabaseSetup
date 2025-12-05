"""
Determine genotype (white/black) from video file path.
"""

from pathlib import Path


def determine_genotype(video_path):
    """
    Determine genotype based on directory structure.
    
    Args:
        video_path: Path to video file (str or Path object)
    
    Returns:
        'white' or 'black' based on parent directory, or None if not found
    
    Example:
        "/path/to/SplitVideos/WhiteAnimals10X/FoodOnly/video.mp4" → 'white'
        "/path/to/SplitVideos/BlackAnimals/ToyOnly/video.mp4" → 'black'
    """
    path_str = str(video_path).lower()
    
    if 'whiteanimals' in path_str:
        return 'white'
    elif 'blackanimals' in path_str:
        return 'black'
    
    return None


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
        # Find a random video
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
    
    # Determine genotype
    genotype = determine_genotype(test_video_path)
    print(f"  → Genotype: {genotype}")
