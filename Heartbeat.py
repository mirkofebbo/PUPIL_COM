import time
import threading

# Send message every 10 second
class Heartbeat:
    def __init__(self, log_data_function, device_system, interval=10):
        self.interval = interval
        self.log_data = log_data_function
        self.device_system = device_system
        self.last_update_time = time.time()

        self.thread = None
        self.stop_event = threading.Event()

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.stop_event.set()
            self.thread.join()
            if self.thread.is_alive():
                print("HEARTBEAT NOT DEAD")
            else:
                print("HEARTBEAT DEAD")

    def _run(self):
        while not self.stop_event.is_set():
            current_time = time.time()
            # This syntax is to make sure a message is indeed being sent even if it is not exactly 10sec
            if current_time - self.last_update_time >= self.interval: 
                u_time = time.time_ns()
                message = "-H-"
                self.log_data(message, u_time)
                self.device_system.send_device_messages(u_time, message) 
                self.last_update_time = current_time

            # Wait for a small amount of time to avoid busy waiting
            time.sleep(0.01)
