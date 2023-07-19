import asyncio
import tkinter as tk
from tkinter import ttk
from pupil_labs.realtime_api import Device, Network
from DeviceHandler import DeviceHandler
import time
# Data loging
import csv
from datetime import datetime
import os
import json
from datetime import datetime
import pytz

data = json.load(open("data/activity.json"))
transitions = [ "PUT_ON_COSTUME", "CHANGE_COSTUME", "REMOVE_COSTUME"]

class App:

    def __init__(self, root, loop):
        self.root = root
        self.handlers = []
        self.loop = loop
        self.device_frame = tk.Frame(self.root)
        self.device_frame.pack(fill=tk.X)
        self.is_any_recording = False 

        self.init_csv_writer()

        self.data = json.load(open("data/activity.json"))
        self.navbar_frame = tk.Frame(self.root)
        self.navbar_frame.pack(fill=tk.X)

        self.discover_button = tk.Button(self.navbar_frame, text="Discover Devices", 
                                        command=self.discover_devices_threadsafe)
        self.discover_button.pack(side=tk.LEFT)  

        self.start_all_button = tk.Button(self.navbar_frame, text="Start Recording All", 
                                        command=self.toggle_recording_all)
        self.start_all_button.pack(side=tk.LEFT)  

        self.activity_frame = tk.Frame(self.root) 
        self.activity_frame.pack(fill=tk.X)  

        self.current_activity = None
        self.current_pnp = None

        tk.Label(self.activity_frame, text="Current activity: ").pack(side=tk.LEFT)

        # Dropdown for selecting date
        self.dates = sorted(list(self.data.keys()))
        self.date_var = tk.StringVar()
        self.date_dropdown = ttk.Combobox(self.activity_frame, textvariable=self.date_var)
        self.date_dropdown['values'] = self.dates
        self.date_dropdown.current(0)  # set selection to first date
        self.date_dropdown.pack(side=tk.LEFT)

        # Update activities when a new date is selected
        self.date_var.trace('w', lambda *args: self.update_activities())

        self.times = sorted(list(next(iter(self.data.values())).keys()))
        self.time_var = tk.StringVar()
        self.time_dropdown = ttk.Combobox(self.activity_frame, textvariable=self.time_var)
        self.time_dropdown['values'] = self.times
        self.time_dropdown.current(0)  # set selection to first time
        self.time_dropdown.pack(side=tk.LEFT)

        # Update activities when a new time is selected
        self.time_var.trace('w', lambda *args: self.update_activities())


        # Update button for activities
        self.activity_button = tk.Button(self.activity_frame, text="Update Activity", command=self.cycle_activity)
        self.activity_button.pack(side=tk.LEFT)
        self.update_activities()  # Set the initial activity

        self.previous_activity = "NONE"
        
        self.custom_frame = tk.Frame(self.root)  
        self.custom_frame.pack(fill=tk.X) 

        self.custom_input = tk.Entry(self.custom_frame)
        self.custom_input.pack(side=tk.LEFT)

        def send_and_clear():
            self.send_message_all(self.custom_input.get(), time.time_ns())
            self.custom_input.delete(0, 'end')

        self.custom_button = tk.Button(self.custom_frame, text="SEND", command=send_and_clear)
        self.custom_button.pack(side=tk.LEFT)

        self.custom_input.bind('<Return>', lambda _: send_and_clear())

        self.laugh_button = tk.Button(self.custom_frame, text="LAUGHING", 
                                    command=lambda: self.send_message_all("LAUGHING", time.time_ns()))
        self.laugh_button.pack(side=tk.LEFT)

        self.talk_button = tk.Button(self.custom_frame, text="PERFORMER_TALK", 
                                    command=lambda: self.send_message_all("PERFORMER_TALK", time.time_ns()))
        self.talk_button.pack(side=tk.LEFT)


        # Create a new frame for transition buttons
        self.transitions_frame = tk.Frame(self.root)
        self.transitions_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add a label to the frame
        label = tk.Label(self.transitions_frame, text="Changes: ")
        label.pack(side=tk.LEFT)
        # Create a button for each transition
        for transition in transitions:
            button = tk.Button(self.transitions_frame, text=transition, 
                            command=lambda transition=transition: self.send_message_all(transition, time.time_ns()))
            button.pack(side=tk.LEFT)
        self.heartbeat()

        self.tasks = []
        

    # ==== DATA LOGGING ====
    def init_csv_writer(self):
        # Initializes a CSV writer with a new file name based on the current time
        data_dir = './data'
        os.makedirs(data_dir, exist_ok=True)
        now = datetime.now()
        filename = f'{data_dir}/PANP_{self.get_next_file_number()}_{now.strftime("%H-%M-%S-%f_%d-%m-%Y")}.csv'
        self.csv_file = open(filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['U_TIME', 'HUMAN_TIME', 'MESSAGE', 'STAGE', "P/NP"])
        self.csv_file_is_open = True

    def get_next_file_number(self):
        # Returns the next performance number based on the existing files in the current directory
        data_dir = './data'
        os.makedirs(data_dir, exist_ok=True)
        files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
        perfo_files = [f for f in files if f.startswith('PANP_')]
        return len(perfo_files) + 1

    def write_to_csv(self, u_time, message, stage, pnp):
        # Check if file is open before writing
        if self.csv_file_is_open:
            human_time = datetime.now().strftime('%H:%M:%S.%f')
            self.csv_writer.writerow([u_time, human_time, message, stage, pnp])

    def close_csv(self):
        if self.csv_file_is_open:
            self.csv_file.close()
            self.csv_file_is_open = False

    #==== ATCIVITY TRACKER ====
    def update_activities(self):
        # Fetch the activities and P/NP status for the selected date and time
        selected_date = self.date_var.get()
        selected_time = self.time_var.get()
        self.activities = self.data[selected_date][selected_time]["activity"]
        self.pnp = self.data[selected_date][selected_time]["P/NP"]

        # Create iterators
        self.activities_iter = iter(self.data[selected_date][selected_time]["activity"])
        self.pnp_iter = iter(self.data[selected_date][selected_time]["P/NP"])

        # Update current activity and P/NP status
        self.cycle_activity()

    def cycle_activity(self):
        try:
            self.current_activity = next(self.activities_iter)
            self.current_pnp = next(self.pnp_iter)
        except StopIteration:  # If end of activities list is reached, start over
            self.activities_iter = iter(self.activities)
            self.pnp_iter = iter(self.p_np)
            self.current_activity = next(self.activities_iter)
            self.current_pnp = next(self.pnp_iter)

        self.activity_button.config(text=f"{self.current_activity} ({self.current_p_np})")  # Update button text

    #==== SENDING MESSAGE ====
    def send_message_all(self, message, u_time):
        # Default message
        formatted_message = f"{message} - Action: {self.current_activity} - P/NP: {self.current_pnp}"

        for handler in self.handlers:
            task = asyncio.run_coroutine_threadsafe(handler.send_message(formatted_message, u_time), self.loop)
            self.tasks.append(task)

        self.write_to_csv(u_time, message, self.current_activity, self.current_pnp)

    def heartbeat(self):
        u_time = time.time_ns()
        # This function sends a heartbeat message to all devices every 10 seconds
        self.send_message_all("H", u_time)
        # Schedule the next heartbeat for 10 seconds from now
        self.heartbeat_id = self.root.after(10000, self.heartbeat)        # Note that because it is using the Tkinter event loop to schedule the heartbeat function, 
        # the function itself doesn't need to be threadsafe. 
        # The after method is the standard way to schedule recurring events in Tkinter.
        # self.write_to_csv(u_time, "H", "STAGE TEST")

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

    def create_transition_buttons(self):
        for transition in transitions:
            self.transition_buttons[transition] = tk.Button(self.transition_frame, text=transition,
                                                            command=lambda transition=transition: self.toggle_transition(transition))
            self.transition_buttons[transition].pack(side=tk.LEFT)

    def toggle_transition(self, transition):
        # Turn off all transitions
        for button in self.transition_buttons.values():
            button.config(relief=tk.RAISED)

        # Turn on selected transition
        self.transition_buttons[transition].config(relief=tk.SUNKEN)
        self.transition_var.set(transition)

        # Send message
        message = "T"
        u_time = time.time_ns()
        self.send_message_all(message, u_time)
    # ==== DEVICE DISPLAY ====
    async def get_device_info(self):
        return [await handler.get_info() for handler in sorted(self.handlers, key=lambda handler: handler.dev_info.name)]

    def display_devices(self, devices_info):
        # Clear previous device labels
        for widget in self.device_frame.winfo_children():
            widget.destroy()

        # Sort the device handlers by device name before displaying
        self.handlers.sort(key=lambda handler: handler.dev_info.name)

        # Display current list of devices
        for i, device_info in enumerate(devices_info):

            # Creating a new function here creates a closure that keeps the values of `handler` and `record_button` 
            def make_button(handler):
                record_button = tk.Button(self.device_frame, text="Start Recording",
                                command=lambda: self.toggle_recording(self.handlers[i], record_button))
                record_button.grid(row=i, column=0)  # put the button on the left

                self.handlers[i].record_button = record_button

                return record_button

            make_button(self.handlers[i])

            device_label = tk.Label(self.device_frame, text=device_info)
            device_label.grid(row=i, column=1)  # put the text on the right

            
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

