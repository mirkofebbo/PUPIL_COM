import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
from DeviceThread import DeviceThread
import threading
import time

class DeviceSystem:

    def __init__(self, phone_file_path="data/phone_info.csv"):
        self.phone_file_path            = phone_file_path
        self.device_threads             = []
        self.phone_info_df              = []
        self.devices                    = []
        self.current_device_info        = pd.DataFrame( columns=['LETTER', 'IP', 'BATTERY', 'STORAGE', 'GLASSES_CONNECTED', "RECORDING"])
        self.device_discovery_event     = threading.Event()  # Added stop event to KILL
        self.device_discovery_thread    = threading.Thread(target=self.update_device_ips)
        self.device_discovery_thread.start()

    # Get a list of reachable devices 
    # get device info
    # If the device is already discovered, update the info
    def update_device_ips(self):
        while not self.device_discovery_event.is_set():  # Stop when event is set
                df = pd.DataFrame( columns=['LETTER', 'IP', 'BATTERY', 'STORAGE', 'GLASSES_CONNECTED', "RECORDING"] )
                self.phone_info_df = pd.read_csv(self.phone_file_path, index_col=False)

                def update_ip(df, device_id, new_ip):
                    index = df[df['ID'] == device_id].index[0]
                    df.at[index, 'IP'] = new_ip
                    df.to_csv(self.phone_file_path, index=False)

                list_of_devices = discover_devices(search_duration_seconds=10.0)
                # print(list_of_devices)
                for device in list_of_devices:
                    temp_row = [
                                device.phone_name, device.phone_ip, 
                                f"{device.battery_level_percent}%",
                                f"{round(device.memory_num_free_bytes / 1024**3)}GB", 
                                False,
                                False
                                ]

                    filtered_df = self.phone_info_df[self.phone_info_df['ID'] == device.phone_id]
                    if not filtered_df.empty and filtered_df['IP'].values[0] != device.phone_ip:
                        update_ip(self.phone_info_df, device.phone_id, device.phone_ip)
                    
                    df.loc[len(df)] = temp_row

                self.current_device_info = df   
                self.devices = list_of_devices
                self.start_devices_thread()  # Start threads for newly discovered devices

                # Sleep for 10 seconds before checking for new devices again
                self.device_discovery_event.wait(10)

                # sg.Window.write_event_value('-TABLE-', df.values)

        
    # ======= FUNCTIONS===================================================
    # Iterate over the devices if one is not specify to perform an action 
    def start_devices_thread(self):
        for device in self.devices:
            # Check if a thread already exists for this device
            existing_threads = [dt for dt in self.device_threads if dt.device.phone_id == device.phone_id]
            if not existing_threads:
                device_thread = DeviceThread(device)
                self.device_threads.append(device_thread)

    # THREAD KILLER 
    def stop_device_threads(self, device_id=None):
        # Kill each device thread
        for device_thread in self.device_threads:
            if device_id is None or device_thread.device.phone_id == device_id:
                device_thread.stop_recording()

        # Additionally stop the device discovery thread
        self.device_discovery_event.set()  # Stop the thread
        if self.device_discovery_thread is not None:
                self.device_discovery_thread.join()
                if self.device_discovery_thread.is_alive():
                    print("UPDATE NOT DEAD")
                else:
                    print("UPDATE DEAD")

    # START RECORDING 
    def start_device_recording(self, u_time, device_id=None):
        for device_thread in self.device_threads:
            if device_id is None or device_thread.device.phone_id == device_id:
                device_thread.start_recording()
                device_thread.queue_message("RECORDING START", u_time)
                print("RECORDING STARTED")
                
    # END RECORDING 
    def end_device_recording(self, u_time, device_id=None):
        for device_thread in self.device_threads:
            if device_id is None or device_thread.device.phone_id == device_id:
                device_thread.queue_message("RECORDING END", u_time)
                device_thread.stop_recording()
                print("RECORDING END")

    # SEND MESSAGES 
    def send_device_messages(self, u_time, message, device_id=None):
        for device_thread in self.device_threads:
            if device_id is None or device_thread.device.phone_id == device_id:
                device_thread.queue_message(message, u_time)
                print("MESSAGE SENT")
