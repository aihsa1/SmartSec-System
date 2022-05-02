#   _      ____          _____ _____ _   _  _____
#  | |    / __ \   /\   |  __ \_   _| \ | |/ ____|
#  | |   | |  | | /  \  | |  | || | |  \| | |  __
#  | |   | |  | |/ /\ \ | |  | || | | . ` | | |_ |
#  | |___| |__| / ____ \| |__| || |_| |\  | |__| |_ _ _
#  |______\____/_/    \_\_____/_____|_| \_|\_____(_|_|_)


import PySimpleGUI as sg
import threading
import os
import json


def show_loading_screen(message, done_loading_flag):
    """
    This function is responsible for displaying the loading screen.

    :param message: the message to be displayed on the loading screen
    :type message: str
    """
    w, h = sg.Window.get_screen_size()
    w, h = int(w // 1.8), int(h // 1.8)
    layout = [
        [
            sg.Column(
                [
                    [sg.Text(message, font=("Helvetica", 25))]
                ], element_justification="center"
            )
        ]
    ]

    WINDOW_ICON = json.loads(
    open(os.path.join("Configs", "icons.json")).read()
    )["smartsec"].encode()

    window = sg.Window("Loading", layout, size=(w, h), icon=WINDOW_ICON)

    # EVENT LOOP
    while True:
        event, values = window.read(timeout=200)
        # print(done_loading_flag, flush=True)
        mutex = threading.Lock()
        mutex.acquire()
        if done_loading_flag[0]:
            break
        mutex.release()
        del mutex

        if event == sg.WIN_CLOSED:
            break
    if "mutex" in locals():
        mutex.release()
    window.close()
