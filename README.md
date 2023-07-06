# PUPIL_COM
Mirko Febbo 
Neurolive project 
06/07/2023

# TO DO START =====================================
TEST:
    Loads of devices 
    IS THE THREAD DEAD? Update Maybe ?

TOP:
    UI
    Master Data Frame 
    Double check time echo protocol 

MEDIUM:
    Check if it is recording 
    Check if the glasses are connected 

LOW:
    Make the code otato proof
    Build a Proper app 

# LIBRARY ======================================
PYTHON THREADING LIBRARY:
    https://docs.python.org/3/library/threading.html


PUPIL LAB API DOCUMENTATION:
    https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/index.html

ATEXIT THREAD KILLING FUNCTION:
    The atexit module defines functions to register and unregister cleanup functions. Functions thus registered are automatically executed upon normal interpreter termination. atexit runs these functions in the reverse order in which they were registered; if you register A, B, and C, at interpreter termination time they will be run in the order C, B, A.
    https://docs.python.org/3/library/atexit.html

# FILES ======================================

Main:
    Current testing ground

DeviceSearch: 
    Does a sweep to find nerby devices
    Retrun a list of device and a df with basic status update on the device.

DeviceThread:
    Start a Thread on the start of the recording.
    Using this thread the user can:
        Start/Stop recording 
        send custom message using time echo protocol:
        
        https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/async.html#module-pupil_labs.realtime_api.time_echo

