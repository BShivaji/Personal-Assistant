import screen_brightness_control as sbc

def increase_brightness(step=10):
    try:
        step = step if step is not None else 10  
        current_brightness = sbc.get_brightness()[0]
        new_brightness = min(100, current_brightness + step)
        sbc.set_brightness(new_brightness)
        return f"Brightness increased to {new_brightness}%."
    except Exception as e:
        print(f" Error adjusting brightness: {e}")
        return "Error adjusting brightness."

def decrease_brightness(step=10):
    try:
        step = step if step is not None else 10  
        current_brightness = sbc.get_brightness()[0]
        new_brightness = max(0, current_brightness - step)
        sbc.set_brightness(new_brightness)
        return f"Brightness decreased to {new_brightness}%."
    except Exception as e:
        print(f" Error adjusting brightness: {e}")
        return "Error adjusting brightness."
