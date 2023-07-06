import pandas as pd

from pupil_labs.realtime_api.simple import discover_devices, Device
from DeviceSearch import update_device_ips
from DeviceThread import DeviceThread
import PySimpleGUI as sg

import atexit
import time

phone_file_path = "data/phone_info.csv"
phone_df, devices = update_device_ips()
device_threads = []

print("phone_df", phone_df)
print("devices", devices)

# Iterate over the devices and create DeviceThread instances
def start_devices_thread():
    for index, device in enumerate(devices):
        device_thread = DeviceThread(device)
        device_threads.append(device_thread)

# THREAD KILLER 
def stop_all_device_threads():
    for device_thread in device_threads:
        device_thread.stop_recording()

# START RECORDING 
def start_all_device_recording():
    for device_thread in device_threads:
        device_thread.start_recording()
        device_thread.send_message("RECORDING START TEST", _time= time.time_ns())
        print("RECORDING STARTED")
        
# END RECORDING 
def send_device_messages(message):
    for device_thread in device_threads:
        device_thread.send_message(message, _time= time.time_ns())
        print( "MESSAGE SENT")

# Example usage of the DeviceThread functions
def end_all_device_recording():
    for device_thread in device_threads:
        device_thread.send_message("RECORDING END TEST", _time= time.time_ns())
        device_thread.stop_recording()
        print("RECORDING END")

# time.sleep(5)

# atexit.register(stop_all_device_threads)
# print("THREAD DIED")

# exit()

# Gather list of pupil device on the wifi 
# list_of_devices = discover_devices(search_duration_seconds=2.0)


# Define the window's contents
layout = [
    [sg.Text("Device Manager")],
    [sg.Button('Update Devices'), sg.Button('Start Recording'), sg.Button('Stop Recording')],
    [sg.Output(size=(60,20), key='-OUTPUT-')]
]

# Create the window
window = sg.Window('Device Manager', layout)

# Event loop
while True:
    event, values = window.read()

    # End program if user closes window
    if event == sg.WINDOW_CLOSED:
        break

    # When the user presses a button, you can update devices, start or stop recording
    if event == 'Update Devices':
        window['-OUTPUT-'].update('Updating devices...')
        # Call the function to update devices here

    if event == 'Start Recording':
        window['-OUTPUT-'].update('Starting recording...')
        # Call the function to start recording here

    if event == 'Stop Recording':
        window['-OUTPUT-'].update('Stopping recording...')
        # Call the function to stop recording here

# Finish up by removing from the screen
window.close()
