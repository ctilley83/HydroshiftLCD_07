import hid
import time
import psutil

# Device details
VENDOR_ID = 0x0416
PRODUCT_ID = 0x7399

def send_packet(device, command, data):
    """Send a 64-byte HID packet."""
    packet = [0x01, command, 0x00, 0x00, 0x00] + data
    packet += [0x00] * (64 - len(packet))
    try:
        device.write(packet)
        print(f"Sent command {hex(command)} with data {data}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Failed to send command {hex(command)}: {e}")

def replicate_lconnect_sequence(device, speed_percent):
    """Send the fan control command sequence."""
    send_packet(device, 0x8A, [0x02, 0x01, 0x0D])
    speed_value = max(0, min(speed_percent, 100))
    send_packet(device, 0x8B, [0x02, 0x00, speed_value])
    send_packet(device, 0x81, [0x00, 0x00, 0x00])

def get_cpu_temperature():
    """Retrieve the current CPU package temperature."""
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            for sensor in temps["coretemp"]:
                if "Package" in sensor.label:
                    return sensor.current
        return None
    except Exception as e:
        print(f"Failed to read temperature: {e}")
        return None

def determine_fan_speed(temp):
    """Determine fan speed based on temperature."""
    if temp is None:
        return 30
    if temp < 40:
        return 30
    elif 40 <= temp <= 55:
        return 50
    elif 56 <= temp <= 70:
        return 70
    else:
        return 100

def main():
    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        print("HydroShift fan control started.")

        last_speed = None

        while True:
            temp = get_cpu_temperature()
            speed = determine_fan_speed(temp)

            if speed != last_speed:
                print(f"CPU Temp: {temp}°C → Setting fan speed to {speed}%")
                replicate_lconnect_sequence(device, speed)
                last_speed = speed

            time.sleep(5)

    except Exception as e:
        print(f"Failed to open device: {e}")
    finally:
        device.close()
        print("HydroShift fan control stopped.")

if __name__ == "__main__":
    main()
