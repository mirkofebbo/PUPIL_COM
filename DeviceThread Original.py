from pupil_labs.realtime_api.simple import Device
import threading
import time
import queue

class DeviceThread:

    def __init__(self, device: Device):
        # Start the values
        self.device = device
        self.recording_event = threading.Event()  # Create an event object for recording
        self.message_queue = queue.Queue()  # Create a queue for messages
        self.thread = None
        self.start_time = None  # Add a start_time attribute
        self.ID = device.phone_name

    def start_recording(self):
        if not self.recording_event.is_set():
            self.recording_event.set()  # Set the event flag to True
            self.start_time = time.time()  # Save the current time when recording starts
            self.device.recording_start()
            self.thread = threading.Thread(target=self._process_messages)
            self.thread.start()

    #KILLING THEM SOFTLY 
    # Send the message to the device
    def stop_recording_without_joining(self):
        # Stop the device/thread recording
        if self.recording_event.is_set():
            self.recording_event.clear()  # Set the event flag to False
            self.start_time = None  # Reset start_time when recording stops
            self.device.recording_stop_and_save()
    
    # KILL THE THREAD 
    def join_thread(self):
        if self.thread is not None:
            self.thread.join()
            if self.thread.is_alive():
                print(self.ID,"DEVICE NOT DEAD")
            else:
                print(self.ID, "DEVICE DEAD")

    def _process_messages(self):
        # Process messages in the queue while recording
        while self.recording_event.is_set():
            if not self.message_queue.empty():
                message, u_time = self.message_queue.get()
                self._send_message(message, u_time)

    def queue_message(self, message, u_time):
        # Add a message to the queue
        self.message_queue.put((message, u_time))

    def _send_message(self, message, u_time):
        # Send a message
        try:
            estimate = self.device.estimate_time_offset()
            u_time_offset = estimate.time_offset_ms.mean *1000000  # Convert MS to NS 
            newtime = u_time - u_time_offset
            event = self.device.send_event(f'{message} o:{u_time_offset} t:{u_time}', event_timestamp_unix_ns=newtime)
            # print(event)

        except:
            print(self.ID,'ot found')
