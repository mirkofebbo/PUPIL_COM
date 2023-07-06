import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
from DeviceSearch import update_device_ips
from DeviceThread import DeviceThread

import atexit
import time

phone_file_path = "data/phone_info.csv"
phone_df, devices = update_device_ips()
print("phone_df", phone_df)
print("devices", devices)

# THREAD KILLER 
def stop_all_device_threads():
    for device_thread in device_threads:
        device_thread.stop_recording()

# Create a list to hold the DeviceThread instances
device_threads = []

# Iterate over the devices and create DeviceThread instances
for index, device in enumerate(devices):
    device_thread = DeviceThread(device)
    device_threads.append(device_thread)
    print(index, "DEVICE STARTED")

time.sleep(5)

for device_thread in device_threads:
    device_thread.start_recording()
    device_thread.send_message("RECORDING START TEST", _time= time.time_ns())
    print("RECORDING STARTED")

time.sleep(10)

for device_thread in device_threads:
    device_thread.send_message("TEST", _time= time.time_ns())
    print( "MESSAGE SENT")

time.sleep(10)

# Example usage of the DeviceThread functions
for device_thread in device_threads:
    device_thread.send_message("RECORDING END TEST", _time= time.time_ns())
    device_thread.stop_recording()
    print("RECORDING END")

time.sleep(5)

atexit.register(stop_all_device_threads)
print("THREAD DIED")

exit()

# Gather list of pupil device on the wifi 
# list_of_devices = discover_devices(search_duration_seconds=2.0)

# for device in list_of_devices:
#     print(f"Phone IP address: {device.phone_ip}")
#     print(f"Phone name: {device.phone_name}")
#     print(f"Phone unique ID: {device.phone_id}")

#     print(f"Battery level: {device.battery_level_percent}%")
#     print(f"Battery state: {device.battery_state}")

#     print(f"Free storage: {device.memory_num_free_bytes / 1024**3}GB")
#     print(f"Storage level: {device.memory_state}")

#     print(f"Connected glasses: SN {device.serial_number_glasses}")
#     print(f"Connected scene camera: SN {device.serial_number_scene_cam}")

#     device.close()  # explicitly stop auto-update
