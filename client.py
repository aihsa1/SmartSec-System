import PySimpleGUI as sg
import numpy as np
import cv2
import os
import time
import threading
import socket


model = None
category_index = None
detect_fn = None
paths = None
files = None
labels = None

SERVER_ADDRESS = ("127.0.0.1", 14_000)

MIN_SCORE_THRESH = 0.5
MAX_BOXES_TO_DRAW = 5
MIN_TEST_TIME = 2  # the time take to detect the weapon

INDICAOR_MESSAGES = {
    "confident_found": "Weapon Found!",
    "potential_found": "Potential Weapon Found!",
    "not_found": "No Weapon Found!",
}


#   _______ _____ __  __ ______ _____     _____ _                _____ _____
#  |__   __|_   _|  \/  |  ____|  __ \   / ____| |        /\    / ____/ ____|
#     | |    | | | \  / | |__  | |__) | | |    | |       /  \  | (___| (___
#     | |    | | | |\/| |  __| |  _  /  | |    | |      / /\ \  \___ \\___ \
#     | |   _| |_| |  | | |____| | \ \  | |____| |____ / ____ \ ____) |___) |
#     |_|  |_____|_|  |_|______|_|  \_\  \_____|______/_/    \_\_____/_____/


class Timer:
    def __init__(self, t0=None, t1=None) -> None:
        self._t = time.time()

    def update_time(self) -> None:
        """
        updates the time to the current time
        """
        self._t = time.time()

    def elapsed_time(self) -> float:
        """
        returns the time elapsed since the last update

        :return: time elapsed since the self._t timestamp (t0)
        :rtype: float
        """
        return time.time() - self._t

    def __str__(self) -> str:
        return str(self._t)


#    _____ ____  __  __ __  __
#   / ____/ __ \|  \/  |  \/  |
#  | |   | |  | | \  / | \  / |
#  | |   | |  | | |\/| | |\/| |
#  | |___| |__| | |  | | |  | |
#   \_____\____/|_|  |_|_|  |_|


def communication():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto("hi server".endcode(), SERVER_ADDRESS)
    data , address = s.recvfrom(1024)
    print(data.decode)


#  __          ________ _      _____ ____  __  __ ______    _____  _____ _____  ______ ______ _   _
#  \ \        / /  ____| |    / ____/ __ \|  \/  |  ____|  / ____|/ ____|  __ \|  ____|  ____| \ | |
#   \ \  /\  / /| |__  | |   | |   | |  | | \  / | |__    | (___ | |    | |__) | |__  | |__  |  \| |
#    \ \/  \/ / |  __| | |   | |   | |  | | |\/| |  __|    \___ \| |    |  _  /|  __| |  __| | . ` |
#     \  /\  /  | |____| |___| |___| |__| | |  | | |____   ____) | |____| | \ \| |____| |____| |\  |
#      \/  \/   |______|______\_____\____/|_|  |_|______| |_____/ \_____|_|  \_\______|______|_| \_|


def show_welcome_window():
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
                        sg.Button(button_text="Connect Server & Detect", key="-CONNECT-SERVER-BUTTON-",
                                  tooltip="Connect to the server and detect pistols", focus=False, enable_events=True),
                        sg.Button(button_text="Detect Locally", key="-DETECT-LOCALLY-BUTTON-",
                                  tooltip="Detect pistols locally, without reporting to the server", focus=False, enable_events=True)
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
        if event in ["-CONNECT-SERVER-BUTTON-", "-DETECT-LOCALLY-BUTTON-"]:
            ret = event
            break
    window.close()
    return ret


#   _      ____          _____ _____ _   _  _____
#  | |    / __ \   /\   |  __ \_   _| \ | |/ ____|
#  | |   | |  | | /  \  | |  | || | |  \| | |  __
#  | |   | |  | |/ /\ \ | |  | || | | . ` | | |_ |
#  | |___| |__| / ____ \| |__| || |_| |\  | |__| |_ _ _
#  |______\____/_/    \_\_____/_____|_| \_|\_____(_|_|_)


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
    window = sg.Window("Loading", layout, size=(w, h))

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
    


#   _____ _   _ _____ _______       _      _____ ____________   __  __  ____  _____  ______ _
#  |_   _| \ | |_   _|__   __|/\   | |    |_   _|___  /  ____| |  \/  |/ __ \|  __ \|  ____| |
#    | | |  \| | | |    | |  /  \  | |      | |    / /| |__    | \  / | |  | | |  | | |__  | |
#    | | | . ` | | |    | | / /\ \ | |      | |   / / |  __|   | |\/| | |  | | |  | |  __| | |
#   _| |_| |\  |_| |_   | |/ ____ \| |____ _| |_ / /__| |____  | |  | | |__| | |__| | |____| |____
#  |_____|_| \_|_____|  |_/_/    \_\______|_____/_____|______| |_|  |_|\____/|_____/|______|______|


def initialize_model(done_loading_flag):
    """
    this function initializes the model and necassary paths
    """
    global model, category_index, detect_fn, paths, files, labels
    global tf, label_map_util, viz_utils

    import tensorflow as tf
    from object_detection.utils import label_map_util
    from object_detection.utils import visualization_utils as viz_utils

    paths = {
        'TENSORFLOW': os.path.join('Tensorflow'),
        'WORKSPACE_PATH': os.path.join('Tensorflow', 'workspace'),
        'APIMODEL_PATH': os.path.join('Tensorflow', 'models'),
        'EXPORTED_MODEL_PATH': os.path.join('Tensorflow', 'workspace', 'exported-model'),
        'ANNOTATION_PATH': os.path.join('Tensorflow', 'workspace', 'annotations'),
        'PROTOC_PATH': os.path.join('Tensorflow', 'protoc')
    }
    files = {
        'LABEL_MAP': os.path.join(paths['ANNOTATION_PATH'], "label_map.pbtxt"),
        "EXPORTED_MODEL_PIPELINE": os.path.join(paths["EXPORTED_MODEL_PATH"], "pipeline.config")
    }
    # labels = ["phone", "pistol", "hand"]
    labels = ["pistol"]

    model = tf.saved_model.load(os.path.join(
        paths["EXPORTED_MODEL_PATH"], "saved_model"))
    category_index = label_map_util.create_category_index_from_labelmap(
        files['LABEL_MAP'])
    detect_fn = model.signatures['serving_default']

    # update the done_loading_flag
    mutex = threading.Lock()
    mutex.acquire()
    done_loading_flag[0] = True
    mutex.release()


#   _____  ______ _______ ______ _____ _______ _____ ____  _   _
#  |  __ \|  ____|__   __|  ____/ ____|__   __|_   _/ __ \| \ | |
#  | |  | | |__     | |  | |__ | |       | |    | || |  | |  \| |
#  | |  | |  __|    | |  |  __|| |       | |    | || |  | | . ` |
#  | |__| | |____   | |  | |___| |____   | |   _| || |__| | |\  |
#  |_____/|______|  |_|  |______\_____|  |_|  |_____\____/|_| \_|


def detection_interface(frame):
    """
    This function is responsible for detecting the weapon on the screen - the interface for the deep learning model.
    :param frame: the frame captured from the camera
    :type frame: numpy.ndarray

    :return: the detections dictionary-like object and the frame with the detections drawn on it (detections, frame)
    :rtype: tuple(OrderedDict, numpy.ndarray)
    """
    global model, category_index, detect_fn

    frame_np = np.array(frame)
    input_tensor = tf.convert_to_tensor(frame_np)
    # The model expects a batch of images, so add an axis with `tf.newaxis`
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(
        np.int64)
    label_id_offset = 0
    frame_np_with_detections = frame_np.copy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        frame_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes']+label_id_offset,
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=MAX_BOXES_TO_DRAW,
        min_score_thresh=MIN_SCORE_THRESH,
        agnostic_mode=False)
    return detections, frame_np_with_detections


#    _____ _    _ _   _   _____ _   _ _____ _____ _____       _______ ____  _____
#   / ____| |  | | \ | | |_   _| \ | |  __ \_   _/ ____|   /\|__   __/ __ \|  __ \
#  | |  __| |  | |  \| |   | | |  \| | |  | || || |       /  \  | | | |  | | |__) |
#  | | |_ | |  | | . ` |   | | | . ` | |  | || || |      / /\ \ | | | |  | |  _  /
#  | |__| | |__| | |\  |  _| |_| |\  | |__| || || |____ / ____ \| | | |__| | | \ \
#   \_____|\____/|_| \_| |_____|_| \_|_____/_____\_____/_/    \_\_|  \____/|_|  \_\


def gui_weapon_indicator(window, detections, confident=False) -> None:
    """
    This function is responsible for displaying the weapon indicator on the screen.
    :param window: the window object
    :type window: PySimpleGUI.Window
    :param detections: the detections dictionary-like object
    :type detections: OrderedDict
    :confident: whether the detection is confident or not - checked multiple times frame and detected a gun
    :type confident: bool

    :return: True if the weapon is detected, False otherwise
    :rtype: bool
    """
    global MIN_SCORE_THRESH, INDICAOR_MESSAGES
    if len(detections["detection_scores"][detections["detection_scores"] >= MIN_SCORE_THRESH]) > 0:
        if confident:
            window["-FOUND-INDICATOR-"].Update(
                INDICAOR_MESSAGES["confident_found"])
        else:
            window["-FOUND-INDICATOR-"].Update(
                INDICAOR_MESSAGES["potential_found"])
    elif window["-FOUND-INDICATOR-"].get() != INDICAOR_MESSAGES["not_found"]:
        window["-FOUND-INDICATOR-"].Update(INDICAOR_MESSAGES["not_found"])


#    _____ _    _ _____       __  __          _____ _   _
#   / ____| |  | |_   _|     |  \/  |   /\   |_   _| \ | |
#  | |  __| |  | | | |       | \  / |  /  \    | | |  \| |
#  | | |_ | |  | | | |       | |\/| | / /\ \   | | | . ` |
#  | |__| | |__| |_| |_      | |  | |/ ____ \ _| |_| |\  |
#   \_____|\____/|_____|     |_|  |_/_/    \_\_____|_| \_|


def gui(detection_mode=True):
    """
    this function is responsible for the GUI of the program.
    :param detection_mode: True if the detection mode is enabled, False otherwise.
    :type detection_mode: bool
    """
    global WIDTH_WEBCAM, HEIGHT_WEBCAM, MIN_SCORE_THRESH, MIN_TEST_TIME

    cap = cv2.VideoCapture(0)
    WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    w, h = int(WIDTH_WEBCAM * 1.3), int(HEIGHT_WEBCAM * 1.3)

    layout = [
        [sg.Text("Webcam Feed With Detections", justification="center",
                 font=(*sg.DEFAULT_FONT, "bold underline"), key="-TITLE-")],
        [sg.Text("Weapon Not Found", justification="left",
                 key="-FOUND-INDICATOR-")],
        [sg.Image(filename='', key="-VIDEO-", enable_events=True, size=(WIDTH_WEBCAM, HEIGHT_WEBCAM), pad=(((w - WIDTH_WEBCAM)
                  * 0.5, (h - HEIGHT_WEBCAM) * 0.5, (0, 0))), background_color="black")],
        [sg.VSeparator()],

    ]

    cap = cv2.VideoCapture(0)
    window = sg.Window('SmartSec Client', layout, size=(w, h))

    t0_exists = False
    confident = False

    # EVENT LOOP
    while True:
        ret, frame = cap.read()
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            break

        if detection_mode:
            detections, frame = detection_interface(frame)
            # engage indicator if there are any detections
            if len(detections["detection_scores"][detections["detection_scores"] >= MIN_SCORE_THRESH]) > 0:
                t0_exists = "t0" in locals()
                if not t0_exists:
                    t0 = Timer()
                    confident = False
                else:
                    if t0.elapsed_time() > MIN_TEST_TIME:
                        confident = True
            elif t0_exists:
                del t0
                t0_exists = False
            gui_weapon_indicator(window, detections, confident)

        frame_bytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-VIDEO-"].update(data=frame_bytes)

    cap.release()
    window.close()


#   __  __          _____ _   _
#  |  \/  |   /\   |_   _| \ | |
#  | \  / |  /  \    | | |  \| |
#  | |\/| | / /\ \   | | | . ` |
#  | |  | |/ ____ \ _| |_| |\  |
#  |_|  |_/_/    \_\_____|_| \_|
def main(detection_mode=True):
    """
    this function is responsible for the main execution of the program - integrating between all of the necassary functions.
    """
    event = show_welcome_window()

    # import necassary module if doing detection
    if event is not None and detection_mode:
        # tells the loading screen to close itself since the tf loading is complete. this flag is passed by reference in a list
        done_loading_flag = [False, ]
        loading_thread = threading.Thread(target=initialize_model,
                             args=(done_loading_flag,), daemon=True)
        loading_thread.start()
        show_loading_screen("Loading...", done_loading_flag)
        loading_thread.join()

        # run the main gui with detection + server connection
        #todo: make a thread for the comm and run it
        gui(detection_mode)


if __name__ == "__main__":
    main()
