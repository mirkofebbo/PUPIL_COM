import time

class Heartbeat:
    def __init__(self, log_data_function, device_system, interval=10):
        self.interval = interval
        self.log_data = log_data_function
        self.device_system = device_system
        self.last_update_time = time.time()

    def update(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.interval:
            u_time = time.time_ns()
            message = "H"
            self.log_data(message, u_time)
            self.device_system.send_device_messages(u_time, message)  # Example method, replace with your own
            self.last_update_time = current_time


