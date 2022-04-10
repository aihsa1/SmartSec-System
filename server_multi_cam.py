from Scripts import add_folders_to_path
from Classes.MultiplexedServer import MultiplexedServer
import threading
import PySimpleGUI as sg
from time import sleep
from Screens.detection_gui import generate_detection_gui_server

window = None


def gui(layout, w, h):
    global window
    window = sg.Window("SmartSec Server", layout, size=(w, h))
    while True:
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            print("closing window")
            break
        if event == "-MIC-BUTTON-":
            pass
    window.close()


def main():
    global window
    gui_thread = threading.Thread(target=gui, args=(
        *generate_detection_gui_server(),), daemon=True)
    gui_thread.start()
    m = MultiplexedServer(window)
    while True:
        m.read()
        sleep(0.07)
        if not gui_thread.is_alive():
            break


if __name__ == "__main__":
    main()
