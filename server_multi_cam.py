from Scripts import add_folders_to_path
from Classes.MultiplexedServer import MultiplexedServer
import threading
import multiprocessing
import PySimpleGUI as sg
from time import sleep
from Screens.detection_gui import generate_detection_gui_server, db_alert_gui_server, generate_db_gui_server

window = None


def db_gui(values, headings):
    layout, w, h = generate_db_gui_server(values, headings)

    win = sg.Window("SmartSec DB", layout, size=(w, h))
    while True:
        event, value = win.read(timeout=5)
        if event in (sg.WIN_CLOSED, "-BACK-BUTTON-"):
            break
        if event == '-TABLE-':
            selected_index = value["-TABLE-"][0]
            db_alert_gui_server(selected_index, tuple(
                zip(headings, values[selected_index])), "")  # TODO: ADD AN IMAGE


def _load_data(db):
    print("fetching data")
    data = list(db.find({}, {"img": False}, db_name="SmartSecDB",
                col_name="Pistols", limit=2))
    headings = list(data[0].keys())
    values = [list(v.values()) for v in data]

    p = multiprocessing.Process(target=db_gui, args=(
        values, headings), daemon=True, name="db_gui_process")
    p.start()
    p.join()
    print("db ui is closed")


def server_gui(layout, w, h, db):
    global window
    db_thread = threading.Thread(target=_load_data, args=(
        db,), daemon=True, name="db_load_and_gui_thread")
    is_db_thread_obsolete = False
    window = sg.Window("SmartSec Server", layout, size=(w, h))
    while True:
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            print("closing window")
            break
        if event == "-DB-BUTTON-":
            if not db_thread.is_alive():
                if is_db_thread_obsolete:
                    db_thread = threading.Thread(target=_load_data, args=(
                        db,), daemon=True, name="db_load_and_gui_thread")
                else:
                    is_db_thread_obsolete = True
                db_thread.start()
    window.close()


def main():
    global window
    m = MultiplexedServer(window)
    gui_thread = threading.Thread(target=server_gui, args=(
        *generate_detection_gui_server(), m.db), daemon=True)
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
    # from bson import ObjectId
    # import datetime
    # import multiprocessing
    # data = [[ObjectId('6252f0d6118784a746aa9475'), ['127.0.0.1', 57371], 'uint8', datetime.datetime(2022, 4, 10, 17, 59, 34, 571000)], [ObjectId('6252f0e2118784a746aa9476'), ['127.0.0.1', 57371], 'uint8', datetime.datetime(2022, 4, 10, 17, 59, 46, 481000)], [ObjectId('6252f17f0585945a344776bc'), ['127.0.0.1', 57430], 'uint8', datetime.datetime(2022, 4, 10, 18, 2, 23, 789000)], [ObjectId('6252f2195b802e4a2e0d5bc0'), ['127.0.0.1', 57487],
    #                                                                                                                                                                                                                                                                                                                                                                                          'uint8', datetime.datetime(2022, 4, 10, 18, 4, 57, 427000)], [ObjectId('6252f2305b802e4a2e0d5bc1'), ['127.0.0.1', 57487], 'uint8', datetime.datetime(2022, 4, 10, 18, 5, 16, 797000)], [ObjectId('6252f2385b802e4a2e0d5bc2'), ['127.0.0.1', 57487], 'uint8', datetime.datetime(2022, 4, 10, 18, 5, 22, 675000)], [ObjectId('6252fbcf0273a2cba8e11739'), ['127.0.0.1', 56718], 'uint8', datetime.datetime(2022, 4, 10, 18, 46, 23, 133000)]]
    # headings = ['_id', 'addr', 'dtype', 'date']
    # # db_gui(data, headings)
    # # p = multiprocessing.Process(target=db_gui, args=(data, headings), daemon=True, name="db_gui_process")
    # # p.start()
    # # p.join()
