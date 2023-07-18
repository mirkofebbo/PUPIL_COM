import asyncio
import tkinter as tk
from pupil_labs.realtime_api import Device, Network
from DeviceHandler import DeviceHandler
import time
# Data loging
import csv
from datetime import datetime
import os
class App:

    def __init__(self, root, loop):
        self.root = root
        self.handlers = []
        self.loop = loop
        self.device_frame = tk.Frame(self.root)
        self.device_frame.pack(fill=tk.X) # This line has changed
        
        # Initialize the CSV writer
        self.init_csv_writer()

        self.is_any_recording = False  # State variable to track if any recording is in progress

        # Create a frame for navbar
        self.navbar_frame = tk.Frame(self.root)
        self.navbar_frame.pack(fill=tk.X)  # Fill the X direction
        
        # Discover button
        self.discover_button = tk.Button(self.navbar_frame, text="Discover Devices", 
                                         command=self.discover_devices_threadsafe)
        self.discover_button.pack(side=tk.LEFT) # This line has changed
        
        # Start all button
        self.start_all_button = tk.Button(self.navbar_frame, text="Start Recording All", 
                                          command=self.toggle_recording_all)
        self.start_all_button.pack(side=tk.LEFT) # This line has changed
        
        # Send message button
        message = "Placeholder"
        self.send_button = tk.Button(self.navbar_frame, text="Send Message",
                                     command=lambda: self.send_message_all(message, time.time_ns()))
        self.send_button.pack(side=tk.LEFT) # This line has changed

        # Heartbeat
        self.heartbeat()
        # Keep track of all tasks
        self.tasks = []

    # ==== DATA LOGGING ====
    def init_csv_writer(self):
        # Initializes a CSV writer with a new file name based on the current time
        data_dir = './data'
        os.makedirs(data_dir, exist_ok=True)
        now = datetime.now()
        filename = f'{data_dir}/PERFO_{self.get_next_file_number()}_{now.strftime("%H-%M-%S-%f_%d-%m-%Y")}.csv'
        self.csv_file = open(filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['U_TIME', 'HUMAN_TIME', 'MESSAGE', 'STAGE'])
        self.csv_file_is_open = True

    def get_next_file_number(self):
        # Returns the next performance number based on the existing files in the current directory
        data_dir = './data'
        os.makedirs(data_dir, exist_ok=True)
        files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
        perfo_files = [f for f in files if f.startswith('PERFO_')]
        return len(perfo_files) + 1

    def write_to_csv(self, u_time, message, stage):
        # Check if file is open before writing
        if self.csv_file_is_open:
            human_time = datetime.now().strftime('%H:%M:%S.%f')
            self.csv_writer.writerow([u_time, human_time, message, stage])

    def close_csv(self):
        if self.csv_file_is_open:
            self.csv_file.close()
            self.csv_file_is_open = False

    # ==== SENDING MESSAGE ====
    def send_message_all(self, message, u_time):
        for handler in self.handlers:
            task = asyncio.run_coroutine_threadsafe(handler.send_message(message, u_time), self.loop)            
            self.write_to_csv(u_time, message, "STAGE TEST")
            self.tasks.append(task)

    def send_message(self, handler, message, u_time):
        task = asyncio.run_coroutine_threadsafe(handler.send_message(message, u_time), self.loop)
        # Store the task
        self.tasks.append(task)

    def heartbeat(self):
        u_time = time.time_ns()
        # This function sends a heartbeat message to all devices every 10 seconds
        self.send_message_all("H", u_time)
        # Schedule the next heartbeat for 10 seconds from now
        self.heartbeat_id = self.root.after(10000, self.heartbeat)        # Note that because it is using the Tkinter event loop to schedule the heartbeat function, 
        # the function itself doesn't need to be threadsafe. 
        # The after method is the standard way to schedule recurring events in Tkinter.
        self.write_to_csv(u_time, "H", "STAGE TEST")

    # ==== RECORDING ====
    def toggle_recording_all(self):
        if self.is_any_recording:
            # If any recording is in progress, stop all
            for handler in self.handlers:
                if handler.is_recording:
                    self.toggle_recording(handler, handler.record_button)
            self.start_all_button.config(text="Start Recording All")
            self.is_any_recording = False
        else:
            # If no recording is in progress, start all
            for handler in self.handlers:
                if not handler.is_recording:
                    self.toggle_recording(handler, handler.record_button)
            self.start_all_button.config(text="Stop Recording All")
            self.is_any_recording = True

    def toggle_recording(self, handler, button):
        if handler.is_recording:
            asyncio.run_coroutine_threadsafe(handler.stop_recording(), self.loop)
            handler.is_recording = False
            button.config(text="Start Recording")
        else:
            asyncio.run_coroutine_threadsafe(handler.start_recording(), self.loop)
            handler.is_recording = True
            button.config(text="Stop Recording")

    # ==== DEVICE DISCOVERY ====
    def discover_devices_threadsafe(self):
        # Schedule discover_devices() coroutine to run on the asyncio event loop
        asyncio.run_coroutine_threadsafe(self.discover_devices(), self.loop)
    
    async def discover_devices(self):
        # Use Pupil Labs API to discover devices
        async with Network() as network:
            # loop to search for devices
            while True:
                try:
                    dev_info = await asyncio.wait_for(network.wait_for_new_device(), timeout=5)
                    # Check if device already exists in handlers list using the name
                    print(dev_info.name)

                    if not any(handler.dev_info.name == dev_info.name for handler in self.handlers):
                        handler = DeviceHandler(dev_info)
                        await handler.init_device()  # Initialize the device
                        handler.is_recording = False  # Add a state variable to handler
                        self.handlers.append(handler)

                except asyncio.TimeoutError:
                    # no more devices to be found, break the loop
                    break

        # If no devices found, create a label and return
        if not self.handlers:
            print("No devices could be found! Abort")
            no_device_label = tk.Label(self.device_frame, text="No devices found.")
            no_device_label.pack()
            return

        # If devices found, schedule the display_devices coroutine
        devices_info = await self.get_device_info()  # Get the updated info
        self.root.after(0, self.display_devices, devices_info)  # Schedule on the Tkinter event loop

    # ==== DISPLAY ====
    async def get_device_info(self):
        return [await handler.get_info() for handler in self.handlers]

    def display_devices(self, devices_info):
        # Clear previous device labels
        for widget in self.device_frame.winfo_children():
            widget.destroy()

        # Display current list of devices
        for i, device_info in enumerate(devices_info):
            device_label = tk.Label(self.device_frame, text=device_info)
            device_label.pack()

            # Creating a new function here creates a closure that keeps the values of `handler` and `record_button` 
            def make_button(handler):
                record_button = tk.Button(self.device_frame, text="Start Recording",
                                  command=lambda: self.toggle_recording(self.handlers[i], record_button))
                
                record_button.pack()

                self.handlers[i].record_button = record_button

                return record_button

            make_button(self.handlers[i])

    
    def close(self):
        # Cancel the heartbeat function
        self.root.after_cancel(self.heartbeat_id)
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        # Close the CSV file
        self.close_csv()
        # Then destroy the window
        self.root.destroy()

