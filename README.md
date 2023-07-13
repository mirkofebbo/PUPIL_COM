# PUPIL_COM
Mirko Febbo 
Neurolive project 
06/07/2023

# NOTES:
    Avoid busy waiting: In the _record method of DeviceThread, you use time.sleep(1) in a while loop. This is an example of busy waiting, which consumes a lot of CPU resources. Instead of doing this, consider using a signaling mechanism such as Event objects in the threading module.

    Reduce I/O operations: In the update_device_ips method, you read from and write to a CSV file in a loop. Disk I/O operations are slow and could be a performance bottleneck. Consider reading the file once at the start, updating the DataFrame in memory, and then writing back to the file once all updates are done.

    Use asynchronous programming: If the devices you're communicating with support it, you might benefit from asynchronous I/O operations. This could free up resources while waiting for responses.

    Batch processing: If possible, group operations together rather than performing them individually. For example, sending a batch of messages at once, instead of one-by-one.

# TO DO START
TEST:
    Loads of devices 
    IS THE THREAD DEAD? Update: Maybe ?

BUG:
    Python terminal sometimes never stop, meaning that some threads are still not closing?
        tryed: os.exit() + sys.exit() and exit() none worked
        
TOP:
    Double check time echo protocol 
    Handle device drop

MEDIUM:
    Add static message button for each events 
    Check if the device is recording 
    Check if the glasses are connected 

LOW:
    Make the code potato proof
    Build a Proper app 
    Add recording timer for each device
    
# LIBRARY
PYTHON THREADING LIBRARY:
    https://docs.python.org/3/library/threading.html


PUPIL LAB API DOCUMENTATION:
    https://pupil-labs-realtime-api.readthedocs.io/en/stable/api/index.html

# FILES

Main:
    UI
    Current testing ground

DeviceSearch: 
    Thread that does a sweep to find nerby devices
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

Heartbeat:
    Thread that call to send a message every 10sec 
    