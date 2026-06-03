import threading
import keyboard
from pynput import mouse
import ctypes
import time

from Mappings import load_config
import Inputs 
from Outputs import (decay_thread_stop,stick_decay_loop,right_trigger_pushed,push_right_trigger,push_left_trigger,let_go_left_trigger,let_go_right_trigger,left_trigger_pushed, center_x,center_y)
import Outputs

Inputs.running = True

def run_converter(suppress):
    global keyboard_hook, mouse_listener

    # reset all state before starting
    Inputs.running = True
    Inputs.pressed_keys.clear()
    decay_thread_stop.clear()

    # reset trigger states
    import Outputs
    Outputs.right_trigger_pushed = False
    Outputs.left_trigger_pushed = False
    Outputs.right_trigger_float = 0.0
    Outputs.left_trigger_float = 0.0

    load_config()

    threading.Thread(target=stick_decay_loop, daemon=True).start()

    keyboard_hook = keyboard.hook(Inputs.loop, suppress=suppress)

    mouse_listener = mouse.Listener(
        on_move=Inputs.on_move,
        on_click=Inputs.on_click,
        suppress=suppress
    )
    mouse_listener.start()

    ctypes.windll.user32.SetCursorPos(center_x, center_y)

    while Inputs.running:
        if Outputs.right_trigger_pushed:
            push_right_trigger(0.25)
        else:
            let_go_right_trigger(0.25)
        time.sleep(1 / 180)

        if Outputs.left_trigger_pushed:
            push_left_trigger(0.25)
        else:
            let_go_left_trigger(0.25)
        time.sleep(1 / 180)

    decay_thread_stop.set()

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