from pupil_labs.realtime_api.simple import Device
import time

class DeviceThread:

    def __init__(self, device: Device):
        # Start the values
        self.device = device
        self.start_time = None  # Add a start_time attribute
        self.ID = device.phone_name

    def start_recording(self):
        self.start_time = time.time()  # Save the current time when recording starts
        self.device.recording_start()

    def stop_recording(self):
        self.start_time = None  # Reset start_time when recording stops
        self.device.recording_stop_and_save()

    def send_message(self, message, u_time):
        # Send a message
        try:
            estimate = self.device.estimate_time_offset()
            u_time_offset = estimate.time_offset_ms.mean *1000000  # Convert MS to NS 
            newtime = u_time - u_time_offset
            event = self.device.send_event(f'{message} o:{u_time_offset} t:{u_time}', event_timestamp_unix_ns=newtime)
            # print(event)

        except:
            print(self.ID,'Not found')
