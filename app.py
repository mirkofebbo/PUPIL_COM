import asyncio
import tkinter as tk
from pupil_labs.realtime_api import Device, Network
from DeviceHandler import DeviceHandler
import time
# Data loging
import csv
from datetime import datetime
import os


stages = ["NONE","THE_DANCE","UKULELE", "EATING_DRINKING", "SPOTIFY", "HOOVERING", "DOING_NOTHING", "GRIEF_EXERCISE", "PLANT_CARE", "POEM", "RITUAL_DANCE"]
transitions = [ "PUT_ON_COSTUME", "CHANGE_COSTUME", "REMOVE_COSTUME"]
class App:

    def __init__(self, root, loop):
        self.root = root
        self.handlers = []
        self.loop = loop
        self.device_frame = tk.Frame(self.root)
        self.device_frame.pack(fill=tk.X)  # This line has changed

        # Initialize the CSV writer
        self.init_csv_writer()

        self.is_any_recording = False  # State variable to track if any recording is in progress

        # Create a frame for navbar
        self.navbar_frame = tk.Frame(self.root)
        self.navbar_frame.pack(fill=tk.X)  # Fill the X direction

        # Discover button
        self.discover_button = tk.Button(self.navbar_frame, text="Discover Devices", 
                                         command=self.discover_devices_threadsafe)
        self.discover_button.pack(side=tk.LEFT)  # This line has changed

        # Start all button
        self.start_all_button = tk.Button(self.navbar_frame, text="Start Recording All", 
                                          command=self.toggle_recording_all)
        self.start_all_button.pack(side=tk.LEFT)  # This line has changed

        # Send message button
        message = "Placeholder"
        self.send_button = tk.Button(self.navbar_frame, text="Send Message",
                                     command=lambda: self.send_message_all(message, time.time_ns()))
        self.send_button.pack(side=tk.LEFT)  # This line has changed

        # Stage button
        self.stages_iter = iter(stages)  # Create iterator from stages list
        self.current_stage = next(self.stages_iter)  # Initialize to first stage
        self.stage_button = tk.Button(self.navbar_frame, text=self.current_stage, command=self.cycle_stage)
        self.stage_button.pack(side=tk.LEFT)

        # Transition drop-down menu
        self.transition_var = tk.StringVar(self.navbar_frame)
        self.transition_var.set(transitions[0])  # set the initial value
        # self.transition_menu = tk.OptionMenu(self.navbar_frame, self.transition_var, *transitions)
        # self.transition_menu.pack(side=tk.LEFT)
        self.transition_buttons = {}
        self.transition_frame = tk.Frame(self.root)  # New frame for transition buttons
        self.transition_frame.pack(fill=tk.X)  # Fill the X direction

        tk.Label(self.transition_frame, text="CHANGING").pack(side=tk.LEFT)  # Text on the left

        self.create_transition_buttons()
        
        self.previous_stage = "NONE"
        self.previous_transition = self.transition_var.get()

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

    def cycle_stage(self):
        try:
            self.current_stage = next(self.stages_iter)  # Get next stage
        except StopIteration:
            self.stages_iter = iter(stages)  # Reset iterator
            self.current_stage = next(self.stages_iter)  # Get first stage
        self.stage_button.config(text=self.current_stage)  # Update button text

    #==== SENDING MESSAGE ====
    def send_message_all(self, message, u_time):
        current_transition = self.transition_var.get()

        if self.current_stage != self.previous_stage:
            formatted_message = f"{message} - Action: {self.current_stage}"
            self.previous_stage = self.current_stage
            stage = self.current_stage
        elif current_transition != self.previous_transition:
            formatted_message = f"{message} - Action: {current_transition}"
            self.previous_transition = current_transition
            stage = current_transition
        else:
            # Default message if neither stage nor transition has changed
            formatted_message = f"{message} - Action: {self.previous_stage if self.previous_stage != 'NONE' else self.previous_transition}"
            stage = self.previous_stage if self.previous_stage != 'NONE' else self.previous_transition

        for handler in self.handlers:
            task = asyncio.run_coroutine_threadsafe(handler.send_message(formatted_message, u_time), self.loop)
            self.tasks.append(task)

        self.write_to_csv(u_time, message, stage) 

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
    # ==== DISPLAY ====
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

