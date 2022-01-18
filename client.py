import PySimpleGUI as sg
import tensorflow as tf
import numpy as np
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import cv2
import os
import time


model = None
category_index = None
detect_fn = None
paths = None
files = None
labels = None

MIN_SCORE_THRESH = 0.5
MAX_BOXES_TO_DRAW = 5


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

    def diff(self, other) -> float:
        """
        returns the time delta between two Timer objects
        (other - self)

        :param other: Timer object - initial timestamp
        :type other: Timer
        """
        return self._t - other._t

    def __str__(self) -> str:
        return str(self._t)

#    _____ ____  __  __ __  __
#   / ____/ __ \|  \/  |  \/  |
#  | |   | |  | | \  / | \  / |
#  | |   | |  | | |\/| | |\/| |
#  | |___| |__| | |  | | |  | |
#   \_____\____/|_|  |_|_|  |_|


def communication():
    pass


def initialize_model():
    """
    this function initializes the model and necassary paths
    """
    global model, category_index, detect_fn, paths, files, labels
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


def gui_weapon_indicator(window, detections) -> bool:
    """
    This function is responsible for displaying the weapon indicator on the screen.
    :param window: the window object
    :type window: PySimpleGUI.Window
    :param detections: the detections dictionary-like object
    :type detections: OrderedDict

    :return: True if the weapon is detected, False otherwise
    :rtype: bool
    """
    global MIN_SCORE_THRESH
    if window["-FOUND-INDICATOR-"].get() == "Weapon Not Found" and len(detections["detection_scores"][detections["detection_scores"] >= MIN_SCORE_THRESH]) > 0:
        window["-FOUND-INDICATOR-"].update("Potential Weapon Found")
        return True
    else:
        window["-FOUND-INDICATOR-"].update("Weapon Not Found")
        return False


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
    global WIDTH_WEBCAM, HEIGHT_WEBCAM

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

    # EVENT LOOP

    t0 = Timer()
    positive_detection_counter = 0

    while True:
        ret, frame = cap.read()
        event, value = window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            break

        if detection_mode:
            detections, frame = detection_interface(frame)
            gui_weapon_indicator(window, detections)

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
def main():
    """
    this function is responsible for the main execution of the program - integrating between all of the necassary functions.
    """
    detection_mode = True
    if detection_mode:
        initialize_model()
    gui(detection_mode)


if __name__ == "__main__":
    main()
