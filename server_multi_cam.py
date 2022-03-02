from Scripts import add_classes_to_path
from Classes.MultiplexedServer import MultiplexedServer
import threading
from time import sleep
from Screens.detection_gui import generate_detection_gui_server

def main():
    m = MultiplexedServer()
    # gui_thread = threading.Thread(target=generate_detection_gui_server, daemon=True)
    # gui_thread.start()
    while True:
        m.read()
        sleep(0.07)
    # gui_thread.join()

if __name__ == "__main__":
    main()