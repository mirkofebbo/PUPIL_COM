from pupil_labs.realtime_api.simple import Device
import threading
import time

class DeviceThread:

    def __init__(self, device: Device):
        # Start the values
        self.device = device
        self.recording = False
        self.thread = None
        self.start_time = None  # Add a start_time attribute

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.start_time = time.time()  # Save the current time when recording starts
            self.device.recording_start()
            self.thread = threading.Thread(target=self._record)
            self.thread.start()

    def stop_recording(self):
        # Stop the device/thread recording
        if self.recording:
            self.recording = False
            self.start_time = None  # Reset start_time when recording stops
            self.device.recording_stop_and_save()
            if self.thread is not None:
                self.thread.join()
                if self.thread.is_alive():
                    print("DEVICE NOT DEAD")
                else:
                    print("DEVICE DEAD")

    def _record(self):
        
        while self.recording:
            
            time.sleep(1) 
            
    def send_message(self, message, u_time):
        try:
            estimate = self.device.estimate_time_offset()
            u_time_offset = estimate.time_offset_ms.mean *1000000  # Convert MS to NS 
            newtime = u_time - u_time_offset
            event = self.device.send_event(f'{message} o:{u_time_offset} t:{u_time}', event_timestamp_unix_ns=newtime)
            # print(event)

        except:
            print(f'Device not found')

