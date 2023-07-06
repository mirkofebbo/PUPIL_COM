import pandas as pd
from pupil_labs.realtime_api.simple import discover_devices, Device
phone_file_path = "data/phone_info.csv"

def update_device_ips():
    df = pd.DataFrame( columns=['LETTER', 'IP', 'BATTERY', 'STORAGE', 'GLASSES_CONNECTED', "RECORDING"] )
    # Load the dataframe
    phone_info_df = pd.read_csv(phone_file_path, index_col=False)

    # Function to update IP
    def update_ip(df, device_id, new_ip):
        # Find the index of the row with the given device ID
        index = df[df['ID'] == device_id].index[0]

        # Update the IP address at that index
        df.at[index, 'IP'] = new_ip

        # Save the updated dataframe to the CSV file
        df.to_csv(phone_file_path, index=False)

    # Gather list of pupil device on the wifi 
    list_of_devices = discover_devices(search_duration_seconds=5.0)
    
    for device in list_of_devices:
        temp_row = [device.phone_name, device.phone_ip, 
                    f"{device.battery_level_percent}%",
                    f"{round(device.memory_num_free_bytes / 1024**3)}GB", 
                    False,
                    False]

        # If the device's IP in the dataframe doesn't match the device's actual IP, update it
        if phone_info_df[phone_info_df['ID'] == device.phone_id]['IP'].values[0] != device.phone_ip:
            update_ip(phone_info_df, device.phone_id, device.phone_ip)
        df.loc[len(df)] = temp_row
        print(temp_row)
    return df, list_of_devices
        
        
        

    