import psutil

def get_system_status():
    """Get CPU usage, battery percentage, and charging status."""
    
    cpu_usage = psutil.cpu_percent(interval=1)

    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else "Unknown"
    plugged = "Plugged in" if battery.power_plugged else "Not Plugged in"

    status = f"CPU usage is {cpu_usage} percent. Battery is at {battery_percent} percent and it is {plugged}."
    
    print(status)
    return status
