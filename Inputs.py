import Mappings
from Outputs import click,release,center_y,center_x,mouse_sensitivity,recenter_mouse,mouse_lock,last_known_x,last_known_y
import time
import Outputs  

pressed_keys = set()
pressed_mouse_buttons = set()

def on_click(x, y, button, pressed):
    print(button)
    button_str = str(button).replace("Button.", "")  # "Button.left" -> "left"
    try:
        button_loc = Mappings.lookup_map[str(button)]
    except:
        return
    print(f"b",button_loc)
    if pressed:
        if button_loc:
            click(button_loc)
    else:
        if button_loc:
            release([button_loc])  

running = True
keyboard_hook = None
mouse_listener = None



def on_move(x, y):
        
    if not mouse_lock:
        Outputs.last_known_x = x
        Outputs.last_known_y = y
        return

    if abs(x - center_x) < 5 and abs(y - center_y) < 5:
        return

    dx = x - Outputs.last_known_x
    dy = y - Outputs.last_known_y

    if abs(dx) < 2:
        dx = 0
    if abs(dy) < 2:
        dy = 0

    Outputs.target_x = max(-1.0, min(1.0, dx * mouse_sensitivity))
    Outputs.target_y = max(-1.0, min(1.0, dy * mouse_sensitivity))
    Outputs.last_move_time = time.time()

    recenter_mouse()

    Outputs.last_known_x = center_x
    Outputs.last_known_y = center_y

def loop(event):  
    
    global running,pressed_keys
    name = event.name
    print(pressed_keys)
    if not name:
        return

    if event.event_type == "down":
        pressed_keys.add(name)
    elif event.event_type == "up":
        pressed_keys.discard(name)
        loc = Mappings.lookup_map.get(name)
        if loc:
            release([loc])  

    for x in list(pressed_keys):
        button_loc = Mappings.lookup_map.get(x)
        if button_loc:
            click(button_loc)

    if name == "esc" and event.event_type == "down":
        running = False
        pressed_keys.clear()