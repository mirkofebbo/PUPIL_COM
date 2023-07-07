# PUPIL_COM
Mirko Febbo 
Neurolive project 
06/07/2023

# TO DO START =====================================
TEST:
    Loads of devices 
    IS THE THREAD DEAD? Update Maybe ?

BUG:
    Python terminal sometimes never stop, meaning that some threads are still not closing
    
TOP:
    UI
    Double check time echo protocol 
    Add data maker/csv mega file.
    Handle device drop

MEDIUM:
    Add static message button for each events 
    Check if the device is recording 
    Check if the glasses are connected 

LOW:
    Make the code otato proof
    Build a Proper app 

# LIBRARY ======================================
PYTHON THREADING LIBRARY:
    https://docs.python.org/3/library/threading.html


PUPIL LAB API DOCUMENTATION:
    https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/index.html

# FILES ======================================

Main:
    UI
    Current testing ground

DeviceSearch: 
    Does a sweep to find nerby devices
    Retrun a list of device and a df with basic status update on the device.
    Now included in DeviceSystem 

DeviceSystem:
    A object responsible for all the devices comunication and connection
    Have a constant search for new device every 30 sec 

DeviceThread:
    Start a Thread on the start of the recording.
    Using this thread the user can:
        kill threads
        Start/Stop recording 
        send custom message using time echo protocol:
        https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/async.html#module-pupil_labs.realtime_api.time_echo

