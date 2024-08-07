import json
import os

def load_json_file(jsonFile: str):
    """
    Loads data from a JSON file.

    Args:
        jsonFile (str): The name of the JSON file to load.

    Returns:
        dict: The data loaded from the JSON file.

    Raises:
        FileNotFoundError: If the specified JSON file does not exist.
    """
    if not jsonFile.endswith('.json'):
        jsonFile = jsonFile + ".json"

    input_json = os.path.join('config', jsonFile)

    try:
        # Check if the file exists
        print(input_json)
        if not os.path.exists(input_json):
            raise FileNotFoundError(f"File '{input_json}' not found.")

    except FileNotFoundError as e:
        # Handle the FileNotFoundError
        print(f"Error: {e}")

    with open(input_json, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
        return json_data
