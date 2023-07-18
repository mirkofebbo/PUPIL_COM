# TODO 
HIGH:
- UPDATE Add if changing button just a MESSAGE not duration / or update it for duration like start changing stop changing button? 
- SAVE CSV more often

MEDIUM:
- BUTTON audiance laugh, performer talk to audience, custom message
- NEED UPDATE  update once in a while to see if we still have the phones/ not gettting update while it is called multiple time
- - Then if we loos one lunch 2-3 search see if we can find it again 
- Check if device is recrording using DeviceHandler print_recording [update the function print_recording]

LOW: 
- Work on the UI layout 
- - UPDATED 
- 
DONE
-  Add dropdown menu to log in the current stage 
-  Find a way to link both stage and change so that in the data it show changing continuosly

# Pupil Labs Device Manager

This project provides an interface to discover and control Pupil Labs devices using their Realtime API. It is built with Python's Tkinter for the user interface, and asyncio for managing the asynchronous communication with the devices.

## Features

- Discover Pupil Labs devices on the network
- Start/Stop recording on each individual device
- Start/Stop recording on all devices simultaneously
- Send a message to all devices

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.10+
- Pupil Labs Realtime API package (pip install pupil_labs)

## Usage

- Start the application and click on "Discover Devices" button to discover the Pupil Labs devices in the network.
- The discovered devices are displayed with their name, IP, battery level, and glasses serial number.
- Use "Start Recording" button next to each device to start/stop recording on that specific device.
- Use "Start Recording All" button to start/stop recording on all devices simultaneously.
- Use "Send Message" button to send a predefined message to all devices.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

- Thanks to Pupil Labs for providing the Realtime API


# Explaining the App Class

The `App` class is the main class that drives the functionality of the GUI application. The `App` class makes use of several other components such as `Tkinter` for the GUI, `asyncio` for asynchronous operations, and the `DeviceHandler` class for handling device-related functionalities.

Below is an explanation of each part of the `App` class:

## 1. `__init__(self, root, loop)`: 

This is the constructor for the `App` class. It initializes the main Tkinter root widget, an asyncio event loop, a list to hold `DeviceHandler` instances, and a frame within the main root widget to hold the device information. It also creates and packs a 'Discover Devices' button into the Tkinter root widget.

## 2. `toggle_recording(self, handler, button)`: 

This function controls the recording state of a device. It takes in two arguments: a `DeviceHandler` instance and a Tkinter button. Depending on the current recording state of the device, it will either start or stop the recording and update the text on the button accordingly.

## 3. `send_message(self, handler, message, u_time)`: 

This function is responsible for sending a message to a device. It uses `asyncio` to run the `send_message` coroutine in the `DeviceHandler` class in a threadsafe manner.

## 4. `discover_devices_threadsafe(self)`: 

This function is used to start the discovery of devices in a threadsafe way.

## 5. `async discover_devices(self)`: 

This coroutine uses the Pupil Labs API to discover devices. It will continue to find devices until it times out. It also checks if a device is already in the handlers list before adding it, thereby preventing duplicate devices. Each discovered device is initialized and its recording state is set to `False`.

## 6. `async get_device_info(self)`: 

This coroutine returns a list of device information for each `DeviceHandler` in the handlers list.

## 7. `display_devices(self, devices_info)`: 

This function displays the information of all discovered devices. It first clears the device frame of any previously displayed information. For each device, it creates a label with the device information, a button to start/stop recording, and a button to send a message. It uses closures to bind each button to its specific handler and to maintain the current state of the recording button.

## 8. `if __name__ == "__main__"`: 

This is the entry point of the application when it's run as a script. It creates the main Tkinter root widget and asyncio event loop, then instantiates the `App` class. It also creates and starts a new thread to run the asyncio event loop so that it can run in parallel with the Tkinter mainloop. 

This entire application functions as a simple graphical user interface to interact with Pupil Labs devices. It provides functionalities to discover devices, display device information, start and stop recording on a device, and send a message to a device.
