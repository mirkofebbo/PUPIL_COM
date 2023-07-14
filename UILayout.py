# ui_setup.py
import PySimpleGUI as sg

def UILayout():
    options = ["Option 1", "Option 2", "Option 3"]

    sg.LOOK_AND_FEEL_TABLE['MyCreatedTheme'] = {'BACKGROUND': '#0D0208',
                                            'TEXT': '#00FF41',
                                            'INPUT': '#202729',
                                            'TEXT_INPUT': '#008F11',
                                            'SCROLL': '#008F11',
                                            'BUTTON': ('#0D0208', '#00FF41'),
                                            'PROGRESS': ('#D1826B', '#CC8019'),
                                            'BORDER': 0, 
                                            'SLIDER_DEPTH': 0, 
                                            'PROGRESS_DEPTH': 0,
                                            }

    sg.theme('MyCreatedTheme')
    devices_per_row = 6
    device_elements = []
    for letter in 'ABCDEFGHIJKL':
        device_elements.append([
            sg.Text(letter, key=f'-DEVICE-{letter}-'),
            sg.Text('', key=f'-POWER-{letter}-'),
            sg.Text('', key=f'-SPACE-{letter}-')
        ])

    device_elements_row1 = device_elements[:devices_per_row]
    device_elements_row2 = device_elements[devices_per_row:]

    device_elements_layout = [
        [sg.Column(device_elements_row1), sg.Column(device_elements_row2)]
    ]

    layout = [
            [sg.Text("Device Manager")],
            [sg.Button("Trigger", key="-TRIGGER-"),
            sg.Button('Start Recording', key="-START-REC-"), 
            sg.Button('Stop Recording', key="-STOP-REC-"),
            sg.Button('KILL', key="-KILLING-"),
            ],
            [sg.Button("SEND", key="-SEND-", bind_return_key=True), 
            sg.Input("", key="-MESSAGE-"),
            sg.Button("CHANGING", key="-CHANGING-"),
            sg.Button('Changing Button', key="-CHANGING-BTN-"),  
            ],
            device_elements_layout,
            [sg.Multiline(size=(66,10), key='-LOGBOX-')]
        ]

    return layout
