# PUPIL_COM
# TO DO START =====================================
TEST:
    Loads of devices 
    IS THE THREAD DEAD?

TOP:
    UI
    Master Data Frame 
    Double check time echo protocol 

MEDIUM:


LOW:
    Potato proof
    Build a Proper app 
# TO DO END ======================================

PYTHON THREADING LIBRARY:
    https://docs.python.org/3/library/threading.html


PUPIL LAB API DOCUMENTATION:
    https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/index.html

Main:
    Currently testing ground

DeviceSearch: 
    Does a sweep to find nerby devices
    Retrun a list of device and a df with basic status update on the device.

DeviceThread:
    Start a Thread on the start of the recording.
    Using this thread the user can:
        Start/Stop recording 
        send custom message using time echo protocol:
        
        https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/async.html#module-pupil_labs.realtime_api.time_echo

