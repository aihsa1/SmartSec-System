from Scripts import add_folders_to_path
from Classes.MultiplexedServer import MultiplexedServer
import threading
import PySimpleGUI as sg
from time import sleep
from Screens.detection_gui import generate_detection_gui_server, db_alert_gui_server, generate_db_gui_server

window = None


def db_gui(db):
    print("fetching data")
    data = list(db.find({}, {"img": False}, db_name="SmartSecDB", col_name="Pistols", limit=2))
    headings = list(data[0].keys())
    values = [list(v.values()) for v in data]
    print("displaying")

    layout, w, h = generate_db_gui_server(values, headings)
    window = sg.Window("SmartSec Server", layout, size=(w, h))
    while True:
        event, value = window.read()
        if event in (sg.WIN_CLOSED, "-BACK-BUTTON-"):
            break
        if event == '-TABLE-':
            i = values["-TABLE-"][0]
            print(i)
            db_alert_gui_server(zip(headings, data[i]))


def server_gui(layout, w, h, db):
    global window
    db_thread = threading.Thread(target=db_gui, args=(db,), daemon=True)
    window = sg.Window("SmartSec Server", layout, size=(w, h))
    while True:
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            print("closing window")
            break
        if event == "-DB-BUTTON-":
            if not db_thread.is_alive():
                db_thread.start()
    window.close()


def main():
    global window
    m = MultiplexedServer(window)
    gui_thread = threading.Thread(target=server_gui, args=(*generate_detection_gui_server(), m.db), daemon=True)
    gui_thread.start()
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
