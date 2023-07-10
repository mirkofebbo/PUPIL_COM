import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
import PySimpleGUI as sg
from DeviceSystem import DeviceSystem

import time

device_system = DeviceSystem()
prev_device_info = device_system.current_device_info.copy()  # To keep track of previous state


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
        sg.Button("Trigger",           key="-TRIGGER-"),
        sg.Button('TEST',              key="-TEST-"),
        sg.Button('Start Recording',   key="-START-REC-"), 
        sg.Button('Stop Recording',    key="-STOP-REC-"),
        sg.Button('Kill all',          key="-KILLING-"),
     ],
    [
        sg.Button("SEND",           key="-SEND-", bind_return_key=True), 
        sg.Input("",                key="-MESSAGE-")],
    [sg.Table(values                =   device_system.current_device_info.values.tolist(), 
              headings              =   list(device_system.current_device_info.columns), 
              display_row_numbers   =   False, 
              auto_size_columns     =   False, 
              num_rows              =   12,# NUM OF ITEMS TO HAVE ON THE LIST 
              key                   =   '-TABLE-')],
    
    [sg.Output(size=(60,20),        key='-OUTPUT-')]
]

# Create the window
window = sg.Window('Device Manager', layout)


# Event loop
while True:
    event, values = window.read(timeout=100) 

    # End program if user closes window
    if event == sg.WINDOW_CLOSED:
        device_system.stop_device_threads()
        break

    # KILL all thread
    if event == '-KILLING-':
        device_system.stop_device_threads()

    # UPDATE TABLE ON NEW DATA
    if not device_system.current_device_info.equals(prev_device_info):
        window['-TABLE-'].update(values=[list(row) for row in device_system.current_device_info.values])
        prev_device_info = device_system.current_device_info.copy()
        
    # START THE RECORDING 
    if event == '-START-REC-':
        window['-OUTPUT-'].update('Starting recording...')
        device_system.start_device_recording(u_time = time.time_ns())

    # UPDATE TABLE DATA
    if event == '-DATAFRAME_UPDATED-': # called in DeviceSystem.py
        window['-TABLE-'].update(values=device_system.current_device_info.values.tolist())
        window['-OUTPUT-'].update('NEW DATA')
        window.refresh()


    # STOP THE RECORDING 
    if event == '-STOP-REC-':
        window['-OUTPUT-'].update('Stopping recording...') 
        device_system.end_device_recording(u_time = time.time_ns())

     # SEND CUSTOM MESSAGE 
    if event == "-SEND-" :
        message = values["-MESSAGE-"]
        u_time = time.time_ns()
        device_system.send_device_messages(u_time, message)
        window["-MESSAGE-"].update("")
        window['-OUTPUT-'].update(message) 

    # SEND TRIGGER
    if event == "-TRIGGER-":
        print(device_system.phone_info_df)
        message = values["-MESSAGE-"]
        u_time = time.time_ns()
        device_system.send_device_messages(u_time, message)
        window["-MESSAGE-"].update("")
        window['-OUTPUT-'].update("TRIGGER")   
        

# Finish up by removing from the screen
window.close()

exit()
