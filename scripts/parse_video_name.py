import re
from datetime import datetime

def parse_video_name(video_name):
    """
    Parse Task_MM_DD_YY_HealthCode_Name[optional _Trial#].ext
    
    Extracts task, modulation, date, animal name, and health status.
    
    Modulation handling:
    - If task ends with 'Excitatory' or 'Inhibitory', extracts it as modulation
    - Task is cleaned to remove the modulation suffix
    - Otherwise, modulation is None
    
    Examples:
        FoodLightExcitatory_2_20_25_S1Y_Doc.mp4 → task='FoodLight', modulation='Excitatory'
        FoodLightInhibitory_1_15_25_S1P_A.mp4 → task='FoodLight', modulation='Inhibitory'
        FoodOnly_7_29_25_S1Y_Celery.mp4 → task='FoodOnly', modulation=None
    
    Returns:
        Tuple of (task, modulation, date_str, animal_name, health) or (None, None, None, None, None)
    """
    # Strip extension if present
    base_name = video_name.rsplit('.', 1)[0]

    # Remove any trailing _Trial... pattern
    base_name = re.sub(r'_(?:[Tt]rial)[ _-]?\d+$', '', base_name)

    # Parse the cleaned name
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
        return None, None, None, None, None

    task = pattern.group("task")
    
    # Extract modulation if present
    modulation = None
    if task.endswith('Excitatory'):
        modulation = 'Excitatory'
        task = task[:-len('Excitatory')]
    elif task.endswith('Inhibitory'):
        modulation = 'Inhibitory'
        task = task[:-len('Inhibitory')]
    
    month = int(pattern.group("month"))
    day = int(pattern.group("day"))
    year = int("20" + pattern.group("year"))
    date_str = datetime(year, month, day).strftime("%Y-%m-%d")

    healthcode = pattern.group("healthcode")
    health = "saline" if healthcode.endswith("Y") else "ghrelin"

    name = pattern.group("name")

    return task, modulation, date_str, name, health


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
    task, modulation, date_str, name, health = parse_video_name(test_video_name)
    
    if task:
        print(f"Parsed results:")
        print(f"  Task:       {task}")
        print(f"  Modulation: {modulation if modulation else 'None'}")
        print(f"  Date:       {date_str}")
        print(f"  Animal:     {name}")
        print(f"  Health:     {health}")
    else:
        print(f"Failed to parse: {test_video_name}")
        print(f"Expected format: Task_MM_DD_YY_HealthCode_AnimalName.mp4")
