"""
Extract video metadata (frame count, FPS, dimensions) using OpenCV.
Simple utility functions for video file information.
"""

import cv2
from pathlib import Path


def find_video_path(video_name, video_dirs):
    """
    Search for a video file in multiple directories.
    
    Args:
        video_name: The video filename to find
        video_dirs: List of directory paths to search
    
    Returns:
        Full path to video if found, None otherwise
    """
    for video_dir in video_dirs:
        video_path = Path(video_dir)
        # Search recursively
        for video_file in video_path.rglob(video_name):
            if video_file.is_file():
                return str(video_file)
    return None


def get_video_info(video_path):
    """
    Extract video metadata using OpenCV.
    
    Args:
        video_path: Full path to video file
    
    Returns:
        Tuple of (num_frames, frame_rate, width, height, trial_length) or (None, None, None, None, None) if failed
        trial_length is calculated as num_frames / frame_rate in seconds
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, None, None, None, None
    
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Calculate trial length in seconds
    trial_length = num_frames / frame_rate if frame_rate and frame_rate > 0 else None
    
    return num_frames, frame_rate, width, height, trial_length


# --- Main Test Block ----------------------------------------------------------

if __name__ == "__main__":
    import sys
    import random
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    video_dirs = [
        data_dir / "SplitVideos" / "WhiteAnimals10X",
        data_dir / "SplitVideos" / "WhiteAnimals2X",
    ]
    
    # Get test video: from user input or random selection
    if len(sys.argv) > 1:
        test_video_name = sys.argv[1]
    else:
        # Find a random video
        all_videos = []
        for vdir in video_dirs:
            all_videos.extend(list(Path(vdir).rglob("*.mp4")))
        
        if not all_videos:
            print("No videos found in SplitVideos directory!")
            sys.exit(1)
        
        test_video = random.choice(all_videos)
        test_video_name = test_video.name
    
    print(f"Testing with video: {test_video_name}\n")
    
    # Find and extract video info
    video_path = find_video_path(test_video_name, video_dirs)
    
    if video_path:
        print(f"Found: {video_path}\n")
        num_frames, frame_rate, width, height, trial_length = get_video_info(video_path)
        
        if None not in (num_frames, frame_rate, width, height, trial_length):
            print(f"Video metadata:")
            print(f"  Frames:       {num_frames}")
            print(f"  Frame rate:   {frame_rate:.2f} fps")
            print(f"  Dimensions:   {width}x{height}")
            print(f"  Trial length: {trial_length:.2f} seconds")
        else:
            print("Failed to read video metadata")
    else:
        print(f"Video not found: {test_video_name}")
