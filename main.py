import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
import PySimpleGUI as sg
from DeviceSystem import DeviceSystem
from datetime import date, datetime
import time
import os
from Heartbeat import Heartbeat
from ui_setup import get_layout

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

layout = get_layout()
window = sg.Window("PUPIL V1", layout, keep_on_top=False, location = (705, 125))
heartbeat = Heartbeat(log_data, device_system)

# Event loop
while True:
    event, values = window.read(timeout=100) 

    # End program if user closes window
    if event == sg.WINDOW_CLOSED:
        df.to_csv(file_path, index=False)
        u_time = time.time_ns()
        device_system.end_device_recording(u_time)
        break

    # KILL all thread
    if event == '-KILLING-':
        df.to_csv(file_path, index=False)
        u_time = time.time_ns()
        device_system.end_device_recording(u_time)
        heartbeat.stop()

    # UPDATE TABLE ON NEW DATA
    for device_id, device_info in device_system.current_device_info.items():
        if f'-POWER-{device_id}-' in window.AllKeysDict and f'-SPACE-{device_id}-' in window.AllKeysDict:
            window[f'-POWER-{device_id}-'].update(device_info['BATTERY'])  # Update battery level
            window[f'-SPACE-{device_id}-'].update(device_info['STORAGE'])  # Update storage usage
        
    # START THE RECORDING 
    if event == '-START-REC-':
        message = '-START_REC-'
        u_time = time.time_ns()
        device_system.start_device_recording(u_time)
        log_data(message, u_time)
        heartbeat.start()

    # UPDATE TABLE DATA
    if event == '-DATAFRAME_UPDATED-': # called in DeviceSystem.py
        window['-TABLE-'].update(values=device_system.current_device_info.values.tolist())
        window['-TABLE-'].update(values=[list(row) for row in device_system.current_device_info.values])
        window.refresh()

    # STOP THE RECORDING 
    if event == '-STOP-REC-':
        message = '-STOP_REC-'
        u_time = time.time_ns()
        log_data(message, u_time)
        device_system.end_device_recording(u_time)
        heartbeat.stop()

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

    # DROP DOWN MENU OPTION
    if event == "-COMBO-":
        selected_option = values["-COMBO-"]
        print(f"Selected option: {selected_option}")
        # You can send a message here, e.g.:
        u_time = time.time_ns()
        device_system.send_device_messages(u_time, selected_option)

    # HEARTBEAT UPDATE
    # if(time.time() - heartbeat_update > 10):
    #     message = "H"
    #     log_data(message, time.time())   
    #     heartbeat_update = time.time()

# Finish up by removing from the screen
window.close()
print('yo moma')
exit()
