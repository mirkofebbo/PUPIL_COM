from pupil_labs.realtime_api.simple import discover_devices, Device
from DeviceThread import DeviceThread
import threading
import time

class DeviceSystem:

    def __init__(self, phone_file_path="data/phone_info.csv"):
        self.phone_file_path            = phone_file_path
        self.device_threads             = []
        self.devices                    = []
        self.current_device_info        = {}
        self.device_discovery_event     = threading.Event()
        self.device_discovery_thread    = threading.Thread(target=self.update_device_ips)
        self.device_discovery_thread.start()

    # Get a list of reachable devices 
    # get device info
    # If the device is already discovered, update the info
    def update_device_ips(self):
        while not self.device_discovery_event.is_set():
            list_of_devices = discover_devices(search_duration_seconds=10.0)
            current_device_info = {}

            for device in list_of_devices:
                temp_row = {
                    'IP': device.phone_ip,
                    'BATTERY': f"{device.battery_level_percent}%",
                    'STORAGE': f"{round(device.memory_num_free_bytes / 1024**3)}GB",
                    'GLASSES_CONNECTED': False,
                    'RECORDING': False
                }
                current_device_info[device.phone_name] = temp_row

            self.current_device_info = current_device_info
            self.devices = list_of_devices
            print("list_of_devices")
            self.start_devices_thread()
            self.device_discovery_event.wait(10)
        
    # ======= FUNCTIONS===================================================
    # Iterate over the devices if one is not specify to perform an action 
    def start_devices_thread(self):
        for device in self.devices:
            # Check if a thread already exists for this device
            existing_threads = [dt for dt in self.device_threads if dt.device.phone_id == device.phone_id]
            if not existing_threads:
                device_thread = DeviceThread(device)
                self.device_threads.append(device_thread)

    # START RECORDING 
    def start_device_recording(self, u_time, device_id=None):
        for device_thread in self.device_threads:
            if device_id is None or device_thread.device.phone_id == device_id:
                device_thread.start_recording()
                device_thread.queue_message("RECORDING START", u_time)
                print("RECORDING STARTED")
                
    # END RECORDING / THREAD KILLER 
    def end_device_recording(self, u_time, device_id=None):
        # Send stop command to all devices and threads
        for device_thread in self.device_threads:
            device_thread.stop_recording_without_joining()

        # Now wait for all threads to join
        for device_thread in self.device_threads:
            device_thread.join_thread()


    # SEND MESSAGES 
    def send_device_messages(self, u_time, message, device_id=None):
        for device_thread in self.device_threads:
            if device_id is None or device_thread.device.phone_id == device_id:
                device_thread.queue_message(message, u_time)
        print("MESSAGE SENT TO ALL DEVICES ")

