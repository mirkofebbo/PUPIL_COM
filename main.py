import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
from device_updater import update_device_ips

phone_file_path = "data/phone_info.csv"
print(update_device_ips())

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
