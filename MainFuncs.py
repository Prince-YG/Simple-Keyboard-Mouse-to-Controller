

import keyboard
import vgamepad as vg
import csv
import os
import sys
from pynput import mouse
import pyautogui
import time
import threading
import ctypes

gamepad = vg.VX360Gamepad()

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BUTTON_FILE = os.path.join(BASE_DIR, "buttons.csv")
AXIS_FILE   = os.path.join(BASE_DIR, "axes.csv")

SCREEN_W, SCREEN_H = pyautogui.size()
CENTER_X = SCREEN_W // 2
CENTER_Y = SCREEN_H // 2

LeftStickAxises = [0, 0]
RightStickAxises = [0, 0]

MOUSELOCK = True

pressed_keys = set()
pressed_mouse_buttons = set()

DEFAULT_BUTTONS = {
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
}

DEFAULT_AXES = {
    "LEFT_X_NEG": "",
    "LEFT_X_POS": "",
    "LEFT_Y_NEG": "",
    "LEFT_Y_POS": "",
    "RIGHT_X_NEG": "",
    "RIGHT_X_POS": "",
    "RIGHT_Y_NEG": "",
    "RIGHT_Y_POS": "",
    "LEFT_MOUSE": "0",
    "RIGHT_MOUSE": "0",
}

def save_dict(filename, d):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for k, v in d.items():
            writer.writerow([k, v])

def load_dict(filename, default):
    if not os.path.exists(filename):
        save_dict(filename, default)
        return default.copy()
    d = {}
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                k, v = row
                d[k] = v
    return d

XUSB_GAMEPAD = load_dict(BUTTON_FILE, DEFAULT_BUTTONS)
AXIS_MAP = load_dict(AXIS_FILE, DEFAULT_AXES)

def MapButton(name, mapping):
    XUSB_GAMEPAD[name] = mapping
    save_dict(BUTTON_FILE, XUSB_GAMEPAD)

def MapAxis(name, mapping):
    AXIS_MAP[name] = mapping
    save_dict(AXIS_FILE, AXIS_MAP)

def FindRealated(value):
    for k, v in XUSB_GAMEPAD.items():
        if v == value:
            return k
    return None

def FindRealatedAxis(value):
    for k, v in AXIS_MAP.items():
        if v == value:
            return k
    return None

def Click(button):
    
    global RightTriggerPushed, LeftTriggerPushed
    print(button)
    if button == "XUSB_GAMEPAD_RIGHT_TRIGGER":
        RightTriggerPushed = True
    elif button == "XUSB_GAMEPAD_LEFT_TRIGGER":
        LeftTriggerPushed = True
    else:
        gamepad.press_button(button=getattr(vg.XUSB_BUTTON, button))
        gamepad.update()

def Release(button):
    global RightTriggerPushed, LeftTriggerPushed
    if button == "XUSB_GAMEPAD_RIGHT_TRIGGER":
        RightTriggerPushed = False
    elif button == "XUSB_GAMEPAD_LEFT_TRIGGER":
        LeftTriggerPushed = False
    else:
        gamepad.release_button(button=getattr(vg.XUSB_BUTTON, button))
        gamepad.update()

def MoveLeftStick(button, amount):
    if button == "LEFT_X_NEG":
        LeftStickAxises[0] -= amount
    elif button == "LEFT_X_POS":
        LeftStickAxises[0] += amount
    elif button == "LEFT_Y_NEG":
        LeftStickAxises[1] -= amount
    elif button == "LEFT_Y_POS":
        LeftStickAxises[1] += amount
    else:
        return
    LeftStickAxises[0] = max(-1.0, min(1.0, LeftStickAxises[0]))
    LeftStickAxises[1] = max(-1.0, min(1.0, LeftStickAxises[1]))
    gamepad.left_joystick_float(x_value_float=LeftStickAxises[0], y_value_float=-LeftStickAxises[1])
    gamepad.update()

def MoveRightStick(button, amount):
    if button == "RIGHT_X_NEG":
        RightStickAxises[0] -= amount
    elif button == "RIGHT_X_POS":
        RightStickAxises[0] += amount
    elif button == "RIGHT_Y_NEG":
        RightStickAxises[1] -= amount
    elif button == "RIGHT_Y_POS":
        RightStickAxises[1] += amount
    else:
        return
    RightStickAxises[0] = max(-1.0, min(1.0, RightStickAxises[0]))
    RightStickAxises[1] = max(-1.0, min(1.0, RightStickAxises[1]))
    gamepad.right_joystick_float(x_value_float=RightStickAxises[0], y_value_float=-RightStickAxises[1])
    gamepad.update()

def ReleaseLeftStick(button, amount):
    if button in ("LEFT_X_NEG", "LEFT_X_POS"):
        LeftStickAxises[0] = 0
    elif button in ("LEFT_Y_NEG", "LEFT_Y_POS"):
        LeftStickAxises[1] = 0
    else:
        return
    gamepad.left_joystick_float(LeftStickAxises[0], -LeftStickAxises[1])
    gamepad.update()

def ReleaseRightStick(button, amount):
    if button in ("RIGHT_X_NEG", "RIGHT_X_POS"):
        RightStickAxises[0] = 0
    elif button in ("RIGHT_Y_NEG", "RIGHT_Y_POS"):
        RightStickAxises[1] = 0
    else:
        return
    gamepad.right_joystick_float(RightStickAxises[0], -RightStickAxises[1])
    gamepad.update()

RightTriggerPushed = False
RightTriggerFloat = 0.0

def PushRightTrigger(amount):
    global RightTriggerFloat
    RightTriggerFloat = min(1.0, RightTriggerFloat + amount)
    gamepad.right_trigger(int(RightTriggerFloat * 255))
    gamepad.update()

def LetGoRightTrigger(amount):
    global RightTriggerFloat
    RightTriggerFloat = max(0.0, RightTriggerFloat - amount)
    gamepad.right_trigger(int(RightTriggerFloat * 255))
    gamepad.update()

LeftTriggerPushed = False
LeftTriggerFloat = 0.0

def PushLeftTrigger(amount):
    global LeftTriggerFloat
    LeftTriggerFloat = min(1.0, LeftTriggerFloat + amount)
    gamepad.left_trigger(int(LeftTriggerFloat * 255))
    gamepad.update()

def LetGoLeftTrigger(amount):
    global LeftTriggerFloat
    LeftTriggerFloat = max(0.0, LeftTriggerFloat - amount)
    gamepad.left_trigger(int(LeftTriggerFloat * 255))
    gamepad.update()

smooth_x = 0.0
smooth_y = 0.0
target_x = 0.0
target_y = 0.0
last_move_time = 0.0
last_known_x = CENTER_X
last_known_y = CENTER_Y

MOUSE_SENSITIVITY = 0.05
SMOOTHING_IN      = 0.35
DECAY_RATE        = 0.15
IDLE_THRESHOLD    = 0.05

def recenter_mouse():
    def _do():
        time.sleep(0.001)
        ctypes.windll.user32.SetCursorPos(CENTER_X, CENTER_Y)
    threading.Thread(target=_do, daemon=True).start()

def on_move(x, y):
    global target_x, target_y, last_move_time, last_known_x, last_known_y

    mouse_active = AXIS_MAP.get("LEFT_MOUSE") == "1" or AXIS_MAP.get("RIGHT_MOUSE") == "1"

    if not MOUSELOCK or not mouse_active:
        last_known_x = x
        last_known_y = y
        return

    if abs(x - CENTER_X) < 5 and abs(y - CENTER_Y) < 5:
        return

    dx = x - last_known_x
    dy = y - last_known_y

    if abs(dx) < 2:
        dx = 0
    if abs(dy) < 2:
        dy = 0

    target_x = max(-1.0, min(1.0, dx * MOUSE_SENSITIVITY))
    target_y = max(-1.0, min(1.0, dy * MOUSE_SENSITIVITY))
    last_move_time = time.time()

    recenter_mouse()

    last_known_x = CENTER_X
    last_known_y = CENTER_Y

_decay_thread_stop = threading.Event()
def _stick_decay_loop():
    global smooth_x, smooth_y, target_x, target_y

    while not _decay_thread_stop.is_set():
        idle = (time.time() - last_move_time) > IDLE_THRESHOLD

        if idle:
            target_x *= (1.0 - DECAY_RATE)
            target_y *= (1.0 - DECAY_RATE)
            if abs(target_x) < 0.005:
                target_x = 0.0
            if abs(target_y) < 0.005:
                target_y = 0.0

        smooth_x += (target_x - smooth_x) * SMOOTHING_IN
        smooth_y += (target_y - smooth_y) * SMOOTHING_IN

        right_mouse = AXIS_MAP.get("RIGHT_MOUSE") == "1"
        left_mouse = AXIS_MAP.get("LEFT_MOUSE") == "1"

        if right_mouse:
            gamepad.right_joystick_float(smooth_x, -smooth_y)
            gamepad.update()
        elif left_mouse:
            gamepad.left_joystick_float(smooth_x, -smooth_y)
            gamepad.update()

        time.sleep(1 / 120)

def on_click(x, y, button, pressed):
    strButton = str(button)
    if strButton in ("Button.left", "Button.right"):
        buttonloc = FindRealated(strButton)
        if pressed:
            if buttonloc:
                Click(buttonloc)
        else:
            if buttonloc:
                Release(buttonloc)

running = False

def Loop(event):
    global running
    name = event.name
    print(name)
    if not name:
        return

    if event.event_type == "down":
        pressed_keys.add(name)
    elif event.event_type == "up":
        pressed_keys.discard(name)
        ButtonLocs = FindRealated(name)
        AxisLocs = FindRealatedAxis(name)
        if ButtonLocs:
            Release(ButtonLocs)
        elif AxisLocs:
            ReleaseLeftStick(AxisLocs, 0)
            ReleaseRightStick(AxisLocs, 0)

    for x in list(pressed_keys):
        ButtonLoc = FindRealated(x)
        AxisLoc = FindRealatedAxis(x)
        if ButtonLoc:
            Click(ButtonLoc)
        elif AxisLoc:
            MoveLeftStick(AxisLoc, 0.75)
            MoveRightStick(AxisLoc, 0.75)

    if name == "esc" and event.event_type == "down":
        running = False
        pressed_keys.clear()
keyboard_hook = None
mouse_listener = None

def RunConverter(suppresss):
    global running, keyboard_hook, mouse_listener

    running = True
    pressed_keys.clear()
    _decay_thread_stop.clear()

    threading.Thread(target=_stick_decay_loop, daemon=True).start()

    # store hook so we can stop it later
    keyboard_hook = keyboard.hook(Loop, suppress=suppresss)

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click,suppress=suppresss)
    mouse_listener.start()

    ctypes.windll.user32.SetCursorPos(CENTER_X, CENTER_Y)

    while running:
        if RightTriggerPushed:
            PushRightTrigger(0.25)
        else:
            LetGoRightTrigger(0.25)

        time.sleep(1 / 180)

        if LeftTriggerPushed:
            PushLeftTrigger(0.25)
        else:
            LetGoLeftTrigger(0.25)

        time.sleep(1 / 180)

    _decay_thread_stop.set()

    # CLEANUP (this is what you were missing)
    try:
        if keyboard_hook:
            keyboard.unhook(keyboard_hook)
            keyboard_hook = None
    except:
        pass

    try:
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
    except:
        pass