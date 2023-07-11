import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
import PySimpleGUI as sg
from DeviceSystem import DeviceSystem
from datetime import date, datetime
import time
import os
from Heartbeat import Heartbeat

device_system = DeviceSystem()
prev_device_info = device_system.current_device_info.copy()  # To keep track of previous state

today = date.today()
file_path = f'data/{today}.csv'

if(os.path.exists(file_path)):
    humain_time = time.strftime("%H:%M:%S", time.localtime())
    temp_data = [time.time_ns(), str(humain_time), "-APP-START-"]
    df = pd.read_csv(file_path, index_col=False)
    df.loc[len(df.index)] = temp_data
else:
    humain_time = time.strftime("%H:%M:%S", time.localtime())
    temp_data = [[time.time_ns(), str(humain_time), "-APP-START-"]]
    df = pd.DataFrame(temp_data, columns=['time', 'human time', 'message'])
    df.to_csv(file_path, index=False)


def log_data(message, u_time):
    u_time_sec = u_time / 1e9  # convert nanoseconds to seconds
    dt_object = datetime.fromtimestamp(u_time_sec)  # Create datetime object from timestamp
    human_readable_time = dt_object.strftime("%H:%M:%S:%f")[:12]  # Gets time in HH:MM:SS:ffffff format and slices to HH:MM:SS:ff

    temp_data = [u_time,  human_readable_time, message]
    df.loc[len(df.index)] = temp_data
    window['-LOGBOX-'].print(temp_data)

# ======= USER INTERFACE ======================
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
              key                   =   '-TABLE-')]
]

layout.append([sg.Multiline(size=(66,10), key='-LOGBOX-')])
# Create the window
window = sg.Window("PUPIL V1", layout, keep_on_top=False, location = (705, 125))
heartbeat = Heartbeat(log_data, device_system)

# Event loop
while True:
    event, values = window.read(timeout=100) 

    # End program if user closes window
    if event == sg.WINDOW_CLOSED:
        df.to_csv(file_path, index=False)
        device_system.stop_device_threads()
        break

    # KILL all thread
    if event == '-KILLING-':
        df.to_csv(file_path, index=False)
        device_system.stop_device_threads()

    # UPDATE TABLE ON NEW DATA
    if not device_system.current_device_info.equals(prev_device_info):
        window['-TABLE-'].update(values=[list(row) for row in device_system.current_device_info.values])
        prev_device_info = device_system.current_device_info.copy()
        
    # START THE RECORDING 
    if event == '-START-REC-':
        message = '-START-REC-'
        u_time = time.time_ns()
        device_system.start_device_recording(u_time)
        log_data(message, u_time)

    # UPDATE TABLE DATA
    if event == '-DATAFRAME_UPDATED-': # called in DeviceSystem.py
        window['-TABLE-'].update(values=device_system.current_device_info.values.tolist())
        window.refresh()

    # STOP THE RECORDING 
    if event == '-STOP-REC-':
        message = '-STOP-REC-'
        u_time = time.time_ns()
        log_data(message, u_time)
        device_system.end_device_recording(u_time)

     # SEND CUSTOM MESSAGE 
    if event == "-SEND-" :
        message = "-MESSAGE-" + values["-MESSAGE-"]
        u_time = time.time_ns()
        device_system.send_device_messages(u_time, message)
        log_data(message, u_time)
        window["-MESSAGE-"].update("")

    # SEND TRIGGER
    if event == "-TRIGGER-":
        clicked_time = time.time_ns()
        message = "-TRIGGER-"
        device_system.send_device_messages(clicked_time, message)
        log_data(message, u_time=clicked_time)
        
    # HEARTBEAT UPDATE
    # if(time.time() - heartbeat_update > 10):
    #     message = "H"
    #     log_data(message, time.time())   
    #     heartbeat_update = time.time()

    heartbeat.update()
# Finish up by removing from the screen
window.close()

exit()
