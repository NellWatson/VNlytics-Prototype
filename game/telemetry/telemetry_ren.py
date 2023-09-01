"""renpy
init python in telemetry:
"""

import requests, json
from collections import OrderedDict 

host = "http://localhost:1313"
api_version = "v1"
project_id = "AISagaInternalTest1"
game_id = ""

collected_choice_data = OrderedDict({})
collected_relationship_data = OrderedDict({})
collected_play_data = OrderedDict({})

last_synced_choice_block = OrderedDict({})
last_synced_relationship_block = OrderedDict({})
last_synced_play_block = OrderedDict({})

session = 1
status = ""

label_name = ""

if not renpy.store.persistent.all_game_ids:
    renpy.store.persistent.all_game_ids = []

if not renpy.store.persistent.multiple_id:
    renpy.store.persistent.multiple_id = False

if not renpy.store.persistent.seen_choice_labels:
    renpy.store.persistent.seen_choice_labels = {}

def label_callback(name, via):
    global label_name
    label_name = name

renpy.config.label_callback = label_callback

def check_internet():
    """
    Returns True if Internet connection is present, otherwise, returns False
    """

    try:
        requests.get(host, timeout=10)
        return True
    except requests.ConnectionError as error:
        return False

def setup():
    """
    Start the actual syncing process in a thread so the game doesn't hang.
    """

    renpy.invoke_in_thread(_setup)

def _setup():
    """
    Queries the server to generate a game id that will be used for saving game data.
    """

    global game_id, status

    import platform

    status = "setup"
    os = platform.system()
    resolution = str((renpy.display.get_info().current_w, renpy.display.get_info().current_h))

    if not check_internet():
        game_id = "placeholder"
        return "No Internet connection."

    payload = {
        "platform": os,
        "display_size": resolution,
        "multiple_ids": renpy.store.persistent.multiple_id
    }

    response = requests.post(f"{host}/{api_version}/{project_id}", json=payload)

    game_id = response.json()["data"]["_id"]
    renpy.store.persistent.all_game_ids.append(game_id)
    renpy.store.persistent.multiple_id = True
    renpy.store.persistent.seen_choice_labels[game_id] = set()

    status = ""
