import json


def update_user_settings(path: str):
    try:
        with open(path, "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    # Iterate through each user and add missing fields at the top level
    for user in settings:
        if "random_words_enabled" not in settings[user]:
            settings[user]["random_words_enabled"] = False
        if "random_words" not in settings[user]:
            settings[user]["random_words"] = []

    # Save the updated settings back to the file
    with open(path, "w") as file:
        json.dump(settings, file, indent=4)

    print("Updated settings for all users without modifying existing fields.")


# Example usage:
update_user_settings("ButtsBorg/streamer_settings_cp.json")
