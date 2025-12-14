import os;
import json;
import random;

json_file = 'loops.json'

class Colors:
    WATER = "\033[38;2;30;187;214m"
    SAND = "\033[38;2;242;182;73m"
    GRASS = "\033[38;2;66;204;41m"
    GRASS_FOOD = "\033[38;2;214;91;30m"
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def append_json(filename, new_data):
    data = []

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    print(f"Warning: Existing file {filename} does not contain a JSON list. Overwriting.")
                    data = []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {filename}. Starting fresh.")
            data = []

    data.append(new_data)

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
        print(f"Successfully appended new data to {filename}")

def classify_terrain(t):
    if t < 0.30:
        return [
            f'{Colors.WATER}~{Colors.ENDC}',
            {
                "type": "water",
                "walkable": False
            }
        ]
    elif t < 0.40:
        return [
            f'{Colors.SAND}.{Colors.ENDC}',
            {
                "type": "sand",
                "walkable": True
            }
        ]
    elif t < 0.70 and t > 0.60 and random.randint(0, 100) > 60:
        return [
            f'{Colors.GRASS_FOOD}.{Colors.ENDC}',
            {
                "type": "food",
                "walkable": True
            }
        ]
    else:
        return [
            f'{Colors.GRASS}.{Colors.ENDC}',
            {
                "type": "grass",
                "walkable": True
            }
        ]