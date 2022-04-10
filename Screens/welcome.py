#  __          ________ _      _____ ____  __  __ ______    _____  _____ _____  ______ ______ _   _
#  \ \        / /  ____| |    / ____/ __ \|  \/  |  ____|  / ____|/ ____|  __ \|  ____|  ____| \ | |
#   \ \  /\  / /| |__  | |   | |   | |  | | \  / | |__    | (___ | |    | |__) | |__  | |__  |  \| |
#    \ \/  \/ / |  __| | |   | |   | |  | | |\/| |  __|    \___ \| |    |  _  /|  __| |  __| | . ` |
#     \  /\  /  | |____| |___| |___| |__| | |  | | |____   ____) | |____| | \ \| |____| |____| |\  |
#      \/  \/   |______|______\_____\____/|_|  |_|______| |_____/ \_____|_|  \_\______|______|_| \_|

import PySimpleGUI as sg
from typing import Tuple


def show_welcome_client() -> Tuple[str, bool]:
    """
    This function is responsible for displaying the welcome window.
    :return: Tuple of the event and the detection mode (e, flag)
    :rtype: Tuple[str, bool]
    """
    w, h = sg.Window.get_screen_size()
    w, h = int(w // 1.8), int(h // 1.8)
    layout = [
        [
            sg.Column(
                [
                    [sg.Text(
                        "Welcome to SmartSec - the Pistol Detection App", font=("Helvetica", 25))],
                    [sg.Text("Detect pistols in your surroundings", font=(
                        "Helvetica", 15))],
                    # [
                    #     sg.Text("Server Connection Status: ", font=("Helvetica", 10)), sg.Text(
                    #         "Not Connected", font=("Helvetica", 10), key="-SERVER-STATUS-", text_color="red")
                    # ],
                    [
                        sg.Button(button_text="Connect to Server & Detect", key="-CONNECT-SERVER-BUTTON-",
                                  tooltip="Connect to the server & detect pistols from a video feed", focus=False, enable_events=True),
                        sg.Button(button_text="Detect Locally from Webcam", key="-DETECT-LOCALLY-WEBCAM-BUTTON-",
                                  tooltip="Detect locally using a webcam, without reporting to the server", focus=False, enable_events=True),
                        sg.Checkbox("Detection", default=True, enable_events=True, key="-DETECTION-CHECKBOX-", tooltip="use ML pistol detection or not"),
                        sg.VerticalSeparator(),
                        sg.Button(button_text="Detect Locally from a Video", key="-DETECT-LOCALLY-VIDEO-BUTTON-",
                                  tooltip="Detect pistols locally from a video, without reporting to the server", focus=False, enable_events=True)
                    ],
                ], element_justification="center"
            )
        ]
    ]
    window = sg.Window("Welcome to SmartSec", layout, size=(w, h))

    # EVENT LOOP
    ret = (None, False)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event in ["-CONNECT-SERVER-BUTTON-", "-DETECT-LOCALLY-WEBCAM-BUTTON-", "-DETECT-LOCALLY-VIDEO-BUTTON-"]:
            ret = (event , window["-DETECTION-CHECKBOX-"].Get())
            break
    window.close()
    return ret
