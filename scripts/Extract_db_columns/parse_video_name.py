import re
from datetime import datetime

def parse_video_name(video_name):
    """
    Robustly parse Task_MM_DD_YY_HealthCode_Name[optional _Trial#].ext
    Accepts 'Trial1', 'trial1', 'Trial_1', or 'Trial-1' and ignores it.
    """
    # Strip extension if present
    base_name = video_name.rsplit('.', 1)[0]

    # 1) Pre-clean: remove any trailing _Trial... pattern
    #    Handles: _Trial1, _trial1, _Trial_1, _Trial-1
    base_name = re.sub(r'_(?:[Tt]rial)[ _-]?\d+$', '', base_name)

    # 2) Parse the cleaned name
    pattern = re.match(
        r'^(?P<task>[A-Za-z]+)_'
        r'(?P<month>\d{1,2})_'
        r'(?P<day>\d{1,2})_'
        r'(?P<year>\d{2})_'
        r'(?P<healthcode>(S\d+[PY]|[PY]))_'
        r'(?P<name>[\w]+)$',
        base_name
    )

    if not pattern:
        return None, None, None, None

    task = pattern.group("task")
    month = int(pattern.group("month"))
    day = int(pattern.group("day"))
    year = int("20" + pattern.group("year"))
    date_str = datetime(year, month, day).strftime("%Y-%m-%d")

    healthcode = pattern.group("healthcode")
    health = "saline" if healthcode.endswith("Y") else "ghrelin"

    name = pattern.group("name")

    return task, date_str, name, health


# --- Main Test Block ----------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    # Get test video name from user or use a default example
    if len(sys.argv) > 1:
        test_video_name = sys.argv[1]
    else:
        # Default test example
        test_video_name = "FoodOnly_7_29_25_S1Y_Celery.mp4"
        print(f"No input provided. Testing with example: {test_video_name}\n")
    
    # Parse the video name
    task, date_str, name, health = parse_video_name(test_video_name)
    
    if task:
        print(f"Parsed results:")
        print(f"  Task:   {task}")
        print(f"  Date:   {date_str}")
        print(f"  Animal: {name}")
        print(f"  Health: {health}")
    else:
        print(f"Failed to parse: {test_video_name}")
        print(f"Expected format: Task_MM_DD_YY_HealthCode_AnimalName.mp4")
