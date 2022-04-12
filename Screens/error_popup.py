import PySimpleGUI as sg
import multiprocessing

def _popup(msg):
    sg.Popup(msg, title="Error", keep_on_top=True)

def show_error_popup(msg):
    p = multiprocessing.Process(target=_popup, args=(msg,), daemon=True)
    p.start()
    p.join()

def main():
    show_error_popup("test")

if __name__ == "__main__":
    main()