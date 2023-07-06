# PUPIL_COM
 

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

