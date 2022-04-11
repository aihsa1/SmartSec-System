from Scripts import add_folders_to_path
from Classes.MultiplexedServer import MultiplexedServer
import threading
import PySimpleGUI as sg
from time import sleep
from Screens.detection_gui import generate_detection_gui_server

window = None


def gui(layout, w, h):
    global window
    is_db_thread_alive = False
    window = sg.Window("SmartSec Server", layout, size=(w, h))
    while True:
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            print("closing window")
            break
        if event == "-DB-BUTTON-":
            if not is_db_thread_alive:
                is_db_thread_alive = True
                pass
    window.close()


def main():
    global window
    gui_thread = threading.Thread(target=gui, args=(
        *generate_detection_gui_server(),), daemon=True)
    gui_thread.start()
    m = MultiplexedServer(window)
    t = m.insert_queue_checker()
    while True:
        m.read()
        sleep(0.07)
        if not gui_thread.is_alive():
            break
    m.final_dump_flag = True
    t.join()


if __name__ == "__main__":
    main()
