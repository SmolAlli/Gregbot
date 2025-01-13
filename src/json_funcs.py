import os
import json
from typing import Union
from enum import StrEnum

class StreamerMode(StrEnum):
    add = "add"
    remove = "rm"

def open_file(path: str, empty: dict | list):
    # Check if the file exists, if not create an empty dictionary
    if os.path.exists(path):
        with open(path, "r") as json_file:
            file_info = json.load(json_file)
    else:
        file_info = empty
    return file_info

def save_to_file(path: str, info: dict | list):
    # Saves the dict information into the file given
    with open(path, "w") as json_file:
        json.dump(info, json_file, indent=4)

# type: ignore
def modify_streamer_settings(path: str, mode: StreamerMode, new_entry: dict[str, dict]):
    # Open the settings file and get contents
    settings = open_file(path, {})

    if mode == StreamerMode.add:
        # Add the new entry to the dictionary
        settings.update(new_entry)
    elif mode == StreamerMode.remove:
        # Ensure new_entry contains a single key (which is what we want to remove)
        if isinstance(new_entry, dict):
            for key in new_entry.keys():
                # Use None to avoid KeyError if the key doesn't exist
                settings.pop(key, None)

    # Save the updated dictionary back to the JSON file
    save_to_file(path, settings)


def modify_streamer_values(path: str, channel_name: str, field: str, new_value: int | str):
    # Open the settings file and get contents
    settings = open_file(path, {})

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
    save_to_file(path, settings)
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

def add_ignore_list(path: str, user: str):
    ignored = open_file(path, [])

    # Check if the user is already in the list
    if user in ignored:
        return False
    else:
    # Add the user to the list
        ignored.append(user)
    
    # Save the updated list back to the JSON file
    save_to_file(path, ignored)
    return True

def remove_ignore_list(path: str, user: str):
    ignored = open_file(path, [])

    # Check if the user is in the list
    if user in ignored:
        # Remove the user from the list
        ignored.remove(user)
    else:
        return False
    
    # Save the updated list back to the JSON file
    save_to_file(path, ignored)
    return True
