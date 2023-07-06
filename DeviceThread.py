from pupil_labs.realtime_api.simple import Device
import threading
import time

class DeviceThread:

    def __init__(self, device: Device):
        self.device = device
        self.recording = False
        self.thread = None

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.device.recording_start()
            self.thread = threading.Thread(target=self._record)
            self.thread.start()

    def stop_recording(self):
        if self.recording:
            self.device.recording_stop_and_save()
            self.recording = False
            if self.thread is not None:
                self.thread.join()

    def kill(self):
        self.recording = False

    def _record(self):
        while self.recording:
            # implement your recording logic here
            print("Recording...")
            time.sleep(1)  # This is just an example

    def status_update(self):
        print(self.device.status_updates())
        # temp_row = [self.device.phone_name, self.device.phone_ip, 
        #     f"{self.device.battery_level_percent}%",
        #     f"{round(self.device.memory_num_free_bytes / 1024**3)}GB", 
        #     False,
        #     self.recording ]


    def send_message(self, message, _time):
        try:
            estimate = self.device.estimate_time_offset()
            u_time_offset = estimate.time_offset_ms.mean *1000000  # Convert MS to NS 
            newtime = _time - u_time_offset
            event = self.device.send_event(f'{message} o:{u_time_offset} t:{_time}', event_timestamp_unix_ns=newtime)
            print(event)

        except:
            print(f'Device not found')
