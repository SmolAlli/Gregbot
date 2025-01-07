import os
import json
from typing import Union


# type: ignore
def modify_streamer_settings(path: str, mode: Union["add", "rm"], new_entry: dict[str, dict]):

    # Check if the file exists, if not create an empty dictionary
    if os.path.exists(path):
        with open(path, "r") as json_file:
            settings = json.load(json_file)
    else:
        settings = {}

    if mode == "add":
        # Add the new entry to the dictionary
        settings.update(new_entry)
    elif mode == "rm":
        # Ensure new_entry contains a single key (which is what we want to remove)
        if isinstance(new_entry, dict):
            for key in new_entry.keys():
                # Use None to avoid KeyError if the key doesn't exist
                settings.pop(key, None)

    # Save the updated dictionary back to the JSON file
    with open(path, "w") as json_file:
        json.dump(settings, json_file, indent=4)


def modify_streamer_values(path: str, channel_name: str, field: str, new_value: int | str):
    # Check if the file exists, if not create an empty dictionary
    if os.path.exists(path):
        with open(path, "r") as json_file:
            settings = json.load(json_file)
    else:
        settings = {}

    # Check if the channel exists in settings, then update the specified field
    if channel_name in settings:
        if field in settings[channel_name]:
            settings[channel_name][field] = new_value  # Update the field value
        else:
            print(
                f"Field '{field}' does not exist in the channel '{channel_name}'.")
    else:
        print(f"Channel '{channel_name}' does not exist in the settings.")

    # Save the updated dictionary back to the JSON file
    with open(path, "w") as json_file:
        json.dump(settings, json_file, indent=4)
    print(f"Updated '{field}' for channel '{channel_name}' to {new_value}")


def check_user_exists(path: str, user: str) -> bool:
    if os.path.exists(path):
        with open(path, "r") as json_file:
            settings = json.load(json_file)
    else:
        print("File not found.")
        return False

    for user in settings:
        if user in settings:
            return True
        else:
            return False
