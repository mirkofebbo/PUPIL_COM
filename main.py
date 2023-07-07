import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
import PySimpleGUI as sg
from DeviceSystem import DeviceSystem

import time

device_system = DeviceSystem()

# ======= USER INTERFACE ==============================================
sg.LOOK_AND_FEEL_TABLE['MyCreatedTheme'] = {'BACKGROUND': '#0D0208',
                                        'TEXT': '#00FF41',
                                        'INPUT': '#202729',
                                        'TEXT_INPUT': '#008F11',
                                        'SCROLL': '#008F11',
                                        'BUTTON': ('#0D0208', '#00FF41'),
                                        'PROGRESS': ('#D1826B', '#CC8019'),
                                        'BORDER': 0, 
                                        'SLIDER_DEPTH': 0, 
                                        'PROGRESS_DEPTH': 0,
                                        }

sg.theme('MyCreatedTheme')
# Define the window's contents
layout = [
    [sg.Text("Device Manager")],
    [
     sg.Button('Start Recording', key="-START-REC-"), 
     sg.Button('Stop Recording', key="-STOP-REC-"),
     sg.Button('Kill all', key="-KILLING-"),
     ],
    [sg.Output(size=(60,20), key='-OUTPUT-')]
]

# Create the window
window = sg.Window('Device Manager', layout)

# Event loop
while True:
    event, values = window.read()

    # End program if user closes window
    if event == sg.WINDOW_CLOSED:
        device_system.stop_device_threads()
        break
    # KILL all thread
    if event == '-KILLING-':
        device_system.stop_device_threads()

    # When the user presses a button, you can update devices, start or stop recording
    if event == '-UPDATE-DEVICES-':
        window['-OUTPUT-'].update('Updating devices...')
        phone_df, devices = device_system.update_device_ips()
        device_system.start_devices_thread(u_time = time.time_ns())
        # Call the function to update devices here

    if event == '-START-REC-':
        window['-OUTPUT-'].update('Starting recording...')
        device_system.start_device_recording(u_time = time.time_ns())
        # Call the function to start recording here

    if event == '-STOP-REC-':
        window['-OUTPUT-'].update('Stopping recording...')
        device_system.end_device_recording(u_time = time.time_ns())
        # Call the function to stop recording here

# Finish up by removing from the screen
window.close()


exit()