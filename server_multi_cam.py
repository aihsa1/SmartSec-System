import cv2
import threading
import numpy as np
from time import sleep
import multiprocessing
import PySimpleGUI as sg
import json
import os
from typing import List, Tuple, Any
from Scripts import add_folders_to_path
from Classes.PyMongoInterface import PyMongoInterface
from Classes.MultiplexedServer import MultiplexedServer
from Screens.detection_gui import generate_detection_gui_server, db_alert_gui_server, generate_db_gui_server

window = None
WINDOW_ICON = json.loads(
    open(os.path.join("Configs", "icons.json")).read()
)["smartsec"].encode()


def db_gui(values: List[List[Any]], headings: List[str], images: List[np.ndarray]):
    """
    This function is used to generate and run the gui for viewing the database.
    :param values: The values to be viewed
    :type values: List[List[Any]]
    :param headings: The headings of the values
    :type headings: List[str]
    :param images: The images to be viewed
    :type images: List[np.ndarray]
    """
    layout, w, h = generate_db_gui_server(
        values, headings)  # generate the necessary layout

    win = sg.Window("SmartSec DB", layout, size=(w, h), icon=WINDOW_ICON)
    while True:
        event, value = win.read()
        if event in (sg.WIN_CLOSED, "-BACK-BUTTON-"):
            break
        if event == '-TABLE-':
            selected_index = value["-TABLE-"][0]
            img_bytes = images[selected_index]
            db_alert_gui_server(
                selected_index,
                zip(headings, values[selected_index]),
                img_bytes)


def _load_data(db: PyMongoInterface, limit: int = 20):
    """
    This function is used to load the data from the database.
    :param db: The database to load the data from
    :type db: PyMongoInterface
    :param limit: The limit of the data to be loaded
    :type limit: int
    """
    print("fetching data")
    data = list(db.find({}, {"dtype": False}, db_name="SmartSecDB",
                col_name="Pistols", limit=limit))
    headings = list(data[0].keys())
    headings.remove("img")
    images = [d.pop("img") for d in data]
    values = [list(v.values()) for v in data]

    # run the DB gui on a separate process - tkinter does not like to be run using multithreading
    p = multiprocessing.Process(target=db_gui, args=(
        values, headings, images), daemon=True, name="db_gui_process")
    p.start()
    p.join()
    print("db ui is closed")


def server_gui(layout, w: int, h: int, db: PyMongoInterface):
    """
    This function is used to generate and run the gui for the server.
    :param layout: The layout of the gui
    :param w: The width of the gui
    :type w: int
    :param h: The height of the gui
    :type h: int
    :param db: The database to be used
    :type db: PyMongoInterface
    """
    global window
    # define the db thread
    db_thread = threading.Thread(target=_load_data, args=(
        db,), daemon=True, name="db_load_and_gui_thread")
    # indicates whether the db_thread has already been used
    is_db_thread_obsolete = False

    mutex = threading.Lock()
    mutex.acquire()
    window = sg.Window("SmartSec Server", layout, size=(w, h), icon=WINDOW_ICON)
    mutex.release()
    while True:
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            print("closing window")
            break
        if event == "-DB-BUTTON-":
            # run the db thread if it is not already running
            if not db_thread.is_alive():
                if is_db_thread_obsolete:
                    db_thread = threading.Thread(target=_load_data, args=(
                        db,), daemon=True, name="db_load_and_gui_thread")
                else:
                    is_db_thread_obsolete = True
                db_thread.start()
    window.close()


def main():
    """
    This function is used to run the server.
    """
    global window
    m = MultiplexedServer(None)
    gui_thread = threading.Thread(target=server_gui, args=(
        *generate_detection_gui_server(), m.db), daemon=True)
    gui_thread.start()
    mutex = threading.Lock()
    mutex.acquire()
    m.window = window
    mutex.release()
    t = m.insert_queue_checker()
    while True:
        m.read()
        sleep(0.07)
        if not gui_thread.is_alive():
            break
    m.final_insert_queue_dump()
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
