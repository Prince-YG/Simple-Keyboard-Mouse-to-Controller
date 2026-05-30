import customtkinter as ctk
from PIL import Image
import threading
import time
from pynput import keyboard as pynput_keyboard, mouse as pynput_mouse
import sys
import os
import keyboard
import MainFuncs
from MainFuncs import MapButton, MapAxis, FindRealated, FindRealatedAxis, XUSB_GAMEPAD, AXIS_MAP, RunConverter

app = ctk.CTk()
app.title("Controller Mapper")
app.geometry("400x750")
app.after(100, lambda: app.attributes("-topmost", True))
app.after(200, lambda: app.attributes("-topmost", False))




def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

BASE = resource_path("Images")

button_map = {
    "A": "XUSB_GAMEPAD_A",
    "B": "XUSB_GAMEPAD_B",
    "X": "XUSB_GAMEPAD_X",
    "Y": "XUSB_GAMEPAD_Y",
    "LB": "XUSB_GAMEPAD_LEFT_SHOULDER",
    "RB": "XUSB_GAMEPAD_RIGHT_SHOULDER",
    "LT": "XUSB_GAMEPAD_LEFT_TRIGGER",
    "RT": "XUSB_GAMEPAD_RIGHT_TRIGGER",
    "LS": "XUSB_GAMEPAD_LEFT_THUMB",
    "RS": "XUSB_GAMEPAD_RIGHT_THUMB",
    "DU": "XUSB_GAMEPAD_DPAD_UP",
    "DD": "XUSB_GAMEPAD_DPAD_DOWN",
    "DL": "XUSB_GAMEPAD_DPAD_LEFT",
    "DR": "XUSB_GAMEPAD_DPAD_RIGHT",
}

stick_map = {
    "LEFT(Left Stick)":   "LEFT_X_NEG",
    "RIGHT(Left Stick)":  "LEFT_X_POS",
    "UP(Left Stick)":     "LEFT_Y_NEG",
    "DOWN(Left Stick)":   "LEFT_Y_POS",
    "LEFT(Right Stick)":  "RIGHT_X_NEG",
    "RIGHT(Right Stick)": "RIGHT_X_POS",
    "UP(Right Stick)":    "RIGHT_Y_NEG",
    "DOWN(Right Stick)":  "RIGHT_Y_POS",
}

image_refs = []

SYSTEM_ON = False
SUPPRESS_ON = False
MOUSEcontrolL = False
MOUSEcontrolR = False

def stop_converter():
    MainFuncs.running = False
    keyboard.unhook_all()

    if getattr(MainFuncs, "mouse_listener", None):
        try:
            MainFuncs.mouse_listener.stop()
        except:
            pass
        MainFuncs.mouse_listener = None

def start_converter():
    MainFuncs.running = True
    threading.Thread(target=lambda: RunConverter(SUPPRESS_ON), daemon=True).start()

def sync_system_button():
    toggle_btn.configure(
        text="SYSTEM: ON" if SYSTEM_ON else "SYSTEM: OFF"
    )


def restart_if_running():
    if SYSTEM_ON:
        stop_converter()
        time.sleep(0.05)
        start_converter()


def load_img(path, size=(28, 28)):
    img = Image.open(path).convert("RGBA")
    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
    image_refs.append(ctk_img)
    return ctk_img


def get_current_mapping(name):
    if name in button_map:
        val = XUSB_GAMEPAD.get(button_map[name], "")
        return val if val else None
    elif name in stick_map:
        val = AXIS_MAP.get(stick_map[name], "")
        return val if val else None
    return None


def MapButtonToMapping(btn, name):
    btn.configure(text="Listening...", fg_color=("gray70", "gray30"))
    result = {"value": None, "cancelled": False}

    def on_key(key):
        if key == pynput_keyboard.Key.esc:
            result["cancelled"] = True
            return False
        try:
            result["value"] = key.char
        except AttributeError:
            result["value"] = str(key).replace("Key.", "")
        return False

    def on_click(x, y, button, pressed):
        if pressed:
            result["value"] = str(button)
            return False

    def run():
        with pynput_keyboard.Listener(on_press=on_key) as kl, \
             pynput_mouse.Listener(on_click=on_click) as ml:
            while result["value"] is None and not result["cancelled"]:
                time.sleep(0.01)

        if result["cancelled"]:
            restore_btn_label(btn, name)
            return

        value = result["value"]
        existing_owner = FindRealated(value) or FindRealatedAxis(value)

        if existing_owner:
            btn.configure(
                text=f"Already mapped to {existing_owner}!",
                fg_color=("firebrick", "darkred"),
            )
            app.after(2000, lambda: restore_btn_label(btn, name))
        else:
            if name in stick_map:
                MapAxis(stick_map[name], value)
            elif name in button_map:
                MapButton(button_map[name], value)
            else:
                restore_btn_label(btn, name)
                return

            btn.configure(text=value, fg_color=("green4", "darkgreen"))
            app.after(1500, lambda: restore_btn_label(btn, name))
            restart_if_running()

    threading.Thread(target=run, daemon=True).start()


def restore_btn_label(btn, name):
    mapping = get_current_mapping(name)
    btn.configure(
        text=mapping if mapping else name,
        fg_color=("green4", "darkgreen") if mapping else ("gray75", "gray25"),
    )

Tframe = ctk.CTkFrame(app)
Tframe.pack(padx=20, pady=(16, 8), fill="x")

def toggle_system():
    global SYSTEM_ON
    SYSTEM_ON = not SYSTEM_ON
    sync_system_button()
    if SYSTEM_ON:
        start_converter()
    else:
        stop_converter()


def monitor_converter_state():
    global SYSTEM_ON

    while True:
        time.sleep(1)

        if SYSTEM_ON and not getattr(MainFuncs, "running", False):
            SYSTEM_ON = False
            app.after(0, sync_system_button)
threading.Thread(target=monitor_converter_state, daemon=True).start()
ctk.CTkLabel(Tframe, text="Controller Mapper",
             font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)
toggle_btn = ctk.CTkButton(Tframe, text="SYSTEM: OFF", command=toggle_system)
toggle_btn.pack(pady=4)
ctk.CTkLabel(Tframe,
             text="Press ESC to cancel mapping • Click buttons to bind inputs",
             font=ctk.CTkFont(size=12)).pack(pady=6)

container = ctk.CTkFrame(app, width=400, height=200)
container.pack(padx=20, pady=(0, 16))
container.pack_propagate(False)

Mframe = ctk.CTkScrollableFrame(container, label_text="Button Mappings")
Mframe.pack(fill="both", expand=True)

buttons_config = [
    ("A",  "Xbox_A_button_(B+W) (1).png"),
    ("B",  "Xbox_B_button_(B+W).svg.png"),
    ("X",  "Xbox_X_button_(B+W).svg.png"),
    ("Y",  "Xbox_Y_button_(B+W).svg.png"),
    ("LB", "Xbox_LB_bumper.svg.png"),
    ("RB", "Xbox_RB_bumper.svg.png"),
    ("LT", "Xbox_LT_trigger.svg.png"),
    ("RT", "Xbox_RT_trigger.svg.png"),
    ("LS", "Xbox_Left_stick.svg.png"),
    ("RS", "Xbox_Right_stick.svg.png"),
    ("DU", "Xbox_D-pad__U_.svg__1_.png"),
    ("DD", "Xbox_D-pad__D_.svg__1_.png"),
    ("DL", "Xbox_D-pad__L_.svg__1_.png"),
    ("DR", "Xbox_D-pad__R_.svg__1_.png"),
]

btn_refs = {}

for label, img_file in buttons_config:
    row = ctk.CTkFrame(Mframe, fg_color="transparent")
    row.pack(fill="x", padx=8, pady=4)

    img = load_img(os.path.join(BASE, img_file), size=(28, 28))
    ctk.CTkLabel(row, image=img, text="", width=36).pack(side="left", padx=(4, 8))
    ctk.CTkLabel(row, text=label, width=30, anchor="w",
                 font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 12))

    current = get_current_mapping(label)
    map_btn = ctk.CTkButton(
        row,
        text=current if current else label,
        width=160,
        font=ctk.CTkFont(size=13),
        fg_color=("green4", "darkgreen") if current else ("gray75", "gray25"),
    )
    map_btn.configure(command=lambda b=map_btn, n=label: MapButtonToMapping(b, n))
    map_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
    btn_refs[label] = map_btn

containerS = ctk.CTkFrame(app, width=400, height=200)
containerS.pack(padx=20, pady=(0, 16))
containerS.pack_propagate(False)

Aframe = ctk.CTkScrollableFrame(containerS, label_text="Stick Mappings")
Aframe.pack(fill="both", expand=True)

sticks_config = [
    ("RIGHT(Right Stick)", "XBOX_RIGHT_STICK_RIGHT.png"),
    ("LEFT(Right Stick)",  "XBOX_RIGHT_STICK_LEFT.png"),
    ("UP(Right Stick)",    "XBOX_RIGHT_STICK_UP.png"),
    ("DOWN(Right Stick)",  "XBOX_RIGHT_STICK_DOWN.png"),
    ("RIGHT(Left Stick)",  "XBOX_LEFT_STICK_RIGHT.png"),
    ("LEFT(Left Stick)",   "XBOX_LEFT_STICK_LEFT.png"),
    ("UP(Left Stick)",     "XBOX_LEFT_STICK_UP.png"),
    ("DOWN(Left Stick)",   "XBOX_LEFT_STICK_DOWN.png"),
]

for label, img_file in sticks_config:
    row = ctk.CTkFrame(Aframe, fg_color="transparent")
    row.pack(fill="x", padx=8, pady=4)

    img = load_img(os.path.join(BASE, img_file), size=(28, 28))
    ctk.CTkLabel(row, image=img, text="", width=36).pack(side="left", padx=(4, 8))

    current = get_current_mapping(label)
    btn = ctk.CTkButton(
        row,
        text=current if current else label,
        fg_color=("green4", "darkgreen") if current else ("gray75", "gray25"),
    )
    btn.configure(command=lambda b=btn, n=label: MapButtonToMapping(b, n))
    btn.pack(side="left", fill="x", expand=True, padx=(0, 4))


containerSet = ctk.CTkFrame(app, width=400, height=200)
containerSet.pack(padx=20, pady=(0, 16))
containerSet.pack_propagate(False)

Sframe = ctk.CTkScrollableFrame(containerSet, label_text="Settings")
Sframe.pack(fill="both", expand=True)


def MouseSwitch(mode):
    global MOUSEcontrolL, MOUSEcontrolR
    if mode == "L":
        MOUSEcontrolL = not MOUSEcontrolL
        if MOUSEcontrolL:
            MOUSEcontrolR = False
    elif mode == "R":
        MOUSEcontrolR = not MOUSEcontrolR
        if MOUSEcontrolR:
            MOUSEcontrolL = False

    if MOUSEcontrolL:
        MapAxis("LEFT_MOUSE", "1")
        MapAxis("RIGHT_MOUSE", "0")
    elif MOUSEcontrolR:
        MapAxis("RIGHT_MOUSE", "1")
        MapAxis("LEFT_MOUSE", "0")
    else:
        MapAxis("LEFT_MOUSE", "0")
        MapAxis("RIGHT_MOUSE", "0")

    print(FindRealatedAxis(str(1)))
    LmouseSwitch.configure(text="ON" if FindRealatedAxis(str(1)) == "LEFT_MOUSE" else "OFF")
    RmouseSwitch.configure(text="ON" if FindRealatedAxis(str(1)) == "RIGHT_MOUSE" else "OFF")
   
    restart_if_running()


def toggle_suppress():
    global SUPPRESS_ON
    SUPPRESS_ON = not SUPPRESS_ON
    suppress_btn.configure(text="ON" if SUPPRESS_ON else "OFF")
    restart_if_running()


Rrow = ctk.CTkFrame(Sframe, fg_color="transparent")
Rrow.pack(fill="x", padx=8, pady=5)
RmouseSwitch = ctk.CTkButton(Rrow, text="OFF", width=60, command=lambda: MouseSwitch("R"))
RmouseSwitch.pack(side="left")
ctk.CTkLabel(Rrow, text="Turn on mouse control for Right Stick").pack(side="left", padx=10)

Lrow = ctk.CTkFrame(Sframe, fg_color="transparent")
Lrow.pack(fill="x", padx=8, pady=5)
LmouseSwitch = ctk.CTkButton(Lrow, text="OFF", width=60, command=lambda: MouseSwitch("L"))
LmouseSwitch.pack(side="left")
ctk.CTkLabel(Lrow, text="Turn on mouse control for Left Stick").pack(side="left", padx=10)

LmouseSwitch.configure(text="ON" if FindRealatedAxis(str(1)) == "LEFT_MOUSE" else "OFF")
RmouseSwitch.configure(text="ON" if FindRealatedAxis(str(1)) == "RIGHT_MOUSE" else "OFF")
   

Suprow = ctk.CTkFrame(Sframe, fg_color="transparent")
Suprow.pack(fill="x", padx=8, pady=5)
suppress_btn = ctk.CTkButton(Suprow, text="OFF", width=60, command=toggle_suppress)
suppress_btn.pack(side="left")
ctk.CTkLabel(Suprow, text="Suppress keyboard passthrough").pack(side="left", padx=10)


app.mainloop()