import keyboard
import vgamepad as vg
import json
import os
import sys
from pynput import mouse
import pyautogui
import time
import threading
import ctypes
from collections import defaultdict



if getattr(sys, "frozen", False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

button_file = os.path.join(base_dir, "buttons.json")

screen_w, screen_h = pyautogui.size()
center_x = screen_w // 2
center_y = screen_h // 2

left_stick_axes = [0, 0]
right_stick_axes = [0, 0]

default_config = {
    "buttons": {
        "XUSB_GAMEPAD_DPAD_UP": "",
        "XUSB_GAMEPAD_DPAD_DOWN": "",
        "XUSB_GAMEPAD_DPAD_LEFT": "",
        "XUSB_GAMEPAD_DPAD_RIGHT": "",
        "XUSB_GAMEPAD_START": "",
        "XUSB_GAMEPAD_BACK": "",
        "XUSB_GAMEPAD_LEFT_THUMB": "",
        "XUSB_GAMEPAD_RIGHT_THUMB": "",
        "XUSB_GAMEPAD_LEFT_SHOULDER": "",
        "XUSB_GAMEPAD_RIGHT_SHOULDER": "",
        "XUSB_GAMEPAD_LEFT_TRIGGER": "",
        "XUSB_GAMEPAD_RIGHT_TRIGGER": "",
        "XUSB_GAMEPAD_GUIDE": "",
        "XUSB_GAMEPAD_A": "",
        "XUSB_GAMEPAD_B": "",
        "XUSB_GAMEPAD_X": "",
        "XUSB_GAMEPAD_Y": "",
    },
    "axes": {
        "A_LEFT_X_NEG": "",
        "A_LEFT_X_POS": "",
        "A_LEFT_Y_NEG": "",
        "A_LEFT_Y_POS": "",
        "A_RIGHT_X_NEG": "",
        "A_RIGHT_X_POS": "",
        "A_RIGHT_Y_NEG": "",
        "A_RIGHT_Y_POS": "",
        "A_LEFT_MOUSE": "0",
        "A_RIGHT_MOUSE": "0",
    }
}

lookup_map = None


def open_and_save_file():
    reverse_mappings_dict()
    with open("data.json", "w") as file:
        json.dump(default_config, file, indent=4)


def load_config():
    global default_config
    if os.path.exists("data.json"):
        with open("data.json", "r") as file:
            saved = json.load(file)
            for section in ("buttons", "axes"):
                if section in saved:
                    default_config[section].update(saved[section])
    reverse_mappings_dict()

def reverse_mappings_dict():
    global lookup_map
    lookup_map = {}
    for section, items in default_config.items():
        for gamepad_input, bound_key in items.items():
            if bound_key and bound_key != "0":  # skip "0" = unset
                lookup_map[bound_key] = gamepad_input


def map_button(name, mapping):
    if name.startswith("A"):
        default_config["axes"][name] = mapping
    else:
        default_config["buttons"][name] = mapping
    open_and_save_file()
reverse_mappings_dict()


if __name__ == "__main__":
    

    
    map_button("A_LEFT_X_NEG", "a")
    map_button("A_LEFT_X_POS", "d")
    map_button("A_LEFT_Y_NEG", "w")
    map_button("A_LEFT_Y_POS", "s")


    open_and_save_file()
    load_config()
    reverse_mappings_dict()
    print(lookup_map["a"])
    print(lookup_map["w"])
    print(lookup_map["s"])
    print(lookup_map["d"])