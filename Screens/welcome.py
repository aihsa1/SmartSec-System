#  __          ________ _      _____ ____  __  __ ______    _____  _____ _____  ______ ______ _   _
#  \ \        / /  ____| |    / ____/ __ \|  \/  |  ____|  / ____|/ ____|  __ \|  ____|  ____| \ | |
#   \ \  /\  / /| |__  | |   | |   | |  | | \  / | |__    | (___ | |    | |__) | |__  | |__  |  \| |
#    \ \/  \/ / |  __| | |   | |   | |  | | |\/| |  __|    \___ \| |    |  _  /|  __| |  __| | . ` |
#     \  /\  /  | |____| |___| |___| |__| | |  | | |____   ____) | |____| | \ \| |____| |____| |\  |
#      \/  \/   |______|______\_____\____/|_|  |_|______| |_____/ \_____|_|  \_\______|______|_| \_|

import PySimpleGUI as sg


def show_welcome_client():
    """
    This function is responsible for displaying the welcome window.
    """
    w, h = sg.Window.get_screen_size()
    w, h = int(w // 1.8), int(h // 1.8)
    layout = [
        [
            sg.Column(
                [
                    [sg.Text(
                        "Welcome to SmartSec - the Pistol Detection App", font=("Helvetica", 25))],
                    [sg.Text("This app will detect pistols in your surroundings", font=(
                        "Helvetica", 15))],
                    [
                        sg.Text("Server Connection Status: ", font=("Helvetica", 10)), sg.Text(
                            "Not Connected", font=("Helvetica", 10), key="-SERVER-STATUS-", text_color="red")
                    ],
                    [
                        sg.Button(button_text="Connect Server & Detect from a Webcam", key="-CONNECT-SERVER-BUTTON-",
                                  tooltip="Connect to the server and detect pistols", focus=False, enable_events=True),
                        sg.Button(button_text="Detect Locally Using a Webcam", key="-DETECT-LOCALLY-WEBCAM-BUTTON-",
                                  tooltip="Detect locally using a webcam, without reporting to the server", focus=False, enable_events=True),
                        sg.Button(button_text="Detect Locally from a Video", key="-DETECT-LOCALLY-VIDEO-BUTTON-",
                                  tooltip="Detect pistols locally from a video, without reporting to the server", focus=False, enable_events=True)
                    ],
                ], element_justification="center"
            )
        ]
    ]
    window = sg.Window("Welcome to SmartSec", layout, size=(w, h))

    # EVENT LOOP
    ret = None
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event in ["-CONNECT-SERVER-BUTTON-", "-DETECT-LOCALLY-WEBCAM-BUTTON-"]:
            ret = event
            break
    window.close()
    return ret
