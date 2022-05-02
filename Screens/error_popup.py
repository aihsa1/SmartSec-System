import PySimpleGUI as sg
import multiprocessing
import os
import json



WINDOW_ICON = json.loads(
    open(os.path.join("Configs", "icons.json")).read()
)["smartsec"].encode()


def _popup(msg):
    """
    This method shows a pop message. IT SHOULD BE USED VIA A PROCESS TO ACHIEVE PARALLELISM
    :param msg: the message to be displayed
    :type msg: str
    """
    sg.Popup(msg, title="Error", keep_on_top=True, icon=WINDOW_ICON)

def show_error_popup(msg: str):
    """
    This function initializes and runs the process of an error popup message
    :param msg: the message to be displayed
    :type msg: str
    """
    p = multiprocessing.Process(target=_popup, args=(msg,), daemon=True)
    p.start()
    p.join()

def main():
    show_error_popup("test")

if __name__ == "__main__":
    main()