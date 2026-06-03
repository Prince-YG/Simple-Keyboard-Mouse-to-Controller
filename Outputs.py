import vgamepad as vg
import pyautogui
import threading
import ctypes
import time
import Mappings


gamepad = vg.VX360Gamepad()

sens = 1

right_trigger_pushed = False
right_trigger_float = 0.0

left_trigger_pushed = False
left_trigger_float = 0.0


left_stick_axes = [0, 0]
right_stick_axes = [0, 0]

mouse_lock = True

pressed_keys = set()
pressed_mouse_buttons = set()

screen_w, screen_h = pyautogui.size()
center_x = screen_w // 2
center_y = screen_h // 2

def click(button):
    print(f"button",button)
    global right_trigger_pushed, left_trigger_pushed
    print(button)
    
    if button == "XUSB_GAMEPAD_RIGHT_TRIGGER":
        print("whenthru")
        right_trigger_pushed = True
    elif button == "XUSB_GAMEPAD_LEFT_TRIGGER":
        left_trigger_pushed = True
    elif button.startswith("A"):
        if button == "A_LEFT_X_NEG":
            left_stick_axes[0] -= sens
        elif button == "A_LEFT_X_POS":
            left_stick_axes[0] += sens
        elif button == "A_LEFT_Y_NEG":
            left_stick_axes[1] -= sens
        elif button == "A_LEFT_Y_POS":
            left_stick_axes[1] += sens
        elif button == "A_RIGHT_X_NEG":
            right_stick_axes[0] -= sens
        elif button == "A_RIGHT_X_POS":
            right_stick_axes[0] += sens
        elif button == "A_RIGHT_Y_NEG":
            right_stick_axes[1] -= sens
        elif button == "A_RIGHT_Y_POS":
            right_stick_axes[1] += sens
        else:
            return

        right_stick_axes[0] = max(-1.0, min(1.0, right_stick_axes[0]))
        right_stick_axes[1] = max(-1.0, min(1.0, right_stick_axes[1]))
        gamepad.right_joystick_float(x_value_float=right_stick_axes[0], y_value_float=-right_stick_axes[1])

        left_stick_axes[0] = max(-1.0, min(1.0, left_stick_axes[0]))
        left_stick_axes[1] = max(-1.0, min(1.0, left_stick_axes[1]))
        gamepad.left_joystick_float(x_value_float=left_stick_axes[0], y_value_float=-left_stick_axes[1])

        gamepad.update()
    else:
        gamepad.press_button(button=getattr(vg.XUSB_BUTTON, button))
        gamepad.update()


def release(button):
    print("realsed")
    global right_trigger_pushed, left_trigger_pushed
    button = button[0]
    if button == "XUSB_GAMEPAD_RIGHT_TRIGGER":
        right_trigger_pushed = False
    elif button == "XUSB_GAMEPAD_LEFT_TRIGGER":
        left_trigger_pushed = False
    elif button.startswith("A"):
        if button.startswith("A_LEFT_X"):
            left_stick_axes[0] = 0
        elif button.startswith("A_LEFT_Y"):
            left_stick_axes[1] = 0
        elif button.startswith("A_RIGHT_X"):
            right_stick_axes[0] = 0
        elif button.startswith("A_RIGHT_Y"):
            right_stick_axes[1] = 0
        else:
            return

        right_stick_axes[0] = max(-1.0, min(1.0, right_stick_axes[0]))
        right_stick_axes[1] = max(-1.0, min(1.0, right_stick_axes[1]))
        gamepad.right_joystick_float(x_value_float=right_stick_axes[0], y_value_float=-right_stick_axes[1])

        left_stick_axes[0] = max(-1.0, min(1.0, left_stick_axes[0]))
        left_stick_axes[1] = max(-1.0, min(1.0, left_stick_axes[1]))
        gamepad.left_joystick_float(x_value_float=left_stick_axes[0], y_value_float=-left_stick_axes[1])

        gamepad.update()
    else:
        gamepad.release_button(button=getattr(vg.XUSB_BUTTON, button))
        gamepad.update()


def push_right_trigger(amount):
    global right_trigger_float
    right_trigger_float = min(1.0, right_trigger_float + amount)
    gamepad.right_trigger(int(right_trigger_float * 255))
    gamepad.update()


def let_go_right_trigger(amount):
    global right_trigger_float
    right_trigger_float = max(0.0, right_trigger_float - amount)
    gamepad.right_trigger(int(right_trigger_float * 255))
    gamepad.update()


def push_left_trigger(amount):
    global left_trigger_float
    left_trigger_float = min(1.0, left_trigger_float + amount)
    gamepad.left_trigger(int(left_trigger_float * 255))
    gamepad.update()


def let_go_left_trigger(amount):
    global left_trigger_float
    left_trigger_float = max(0.0, left_trigger_float - amount)
    gamepad.left_trigger(int(left_trigger_float * 255))
    gamepad.update()


smooth_x = 0.0
smooth_y = 0.0
target_x = 0.0
target_y = 0.0
last_move_time = 0.0
last_known_x = center_x
last_known_y = center_y

mouse_sensitivity = 0.05
smoothing_in = 0.35
decay_rate = 0.15
idle_threshold = 0.05


def recenter_mouse():
    def _do():
        time.sleep(0.001)
        ctypes.windll.user32.SetCursorPos(center_x, center_y)
    threading.Thread(target=_do, daemon=True).start()

decay_thread_stop = threading.Event()


def stick_decay_loop():
    global smooth_x, smooth_y, target_x, target_y, last_move_time


    while not decay_thread_stop.is_set():
       
        idle = (time.time() - last_move_time) > idle_threshold

        if idle:
            target_x *= (1.0 - decay_rate)
            target_y *= (1.0 - decay_rate)
            if abs(target_x) < 0.005:
                target_x = 0.0
            if abs(target_y) < 0.005:
                target_y = 0.0

        smooth_x += (target_x - smooth_x) * smoothing_in
        smooth_y += (target_y - smooth_y) * smoothing_in

        right_mouse = Mappings.lookup_map.get("1") == "A_RIGHT_MOUSE" if  Mappings.lookup_map else False
        left_mouse =  Mappings.lookup_map.get("1") == "A_LEFT_MOUSE" if  Mappings.lookup_map else False
        
        if right_mouse:
            gamepad.right_joystick_float(smooth_x, -smooth_y)
            gamepad.update()
        elif left_mouse:
            gamepad.left_joystick_float(smooth_x, -smooth_y)
            gamepad.update()

        time.sleep(1 / 120)

