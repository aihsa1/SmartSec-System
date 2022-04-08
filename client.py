import os
import cv2
import json
import pickle
import hashlib
import threading
import numpy as np
from time import sleep
import PySimpleGUI as sg
from Scripts import add_folders_to_path
from Classes.CommunicationCode import CommunicationCode
from Classes.Timer import Timer
from Classes.Message import Message
from Classes.CustomSocket import ClientSocket
from Classes.RSAEncryption import RSAEncyption
from Classes.AESEncryption import AESEncryption
from Screens.welcome import show_welcome_client
from Screens.loading import show_loading_screen
from Screens.detection_gui import generate_detection_gui_client


model = None
category_index = None
detect_fn = None
paths = None
files = None
labels = None

frame_bytes = None
frame = None
is_cap_open = False
confident = None

SERVER_ADDRESS = ("127.0.0.1", 14_000)

MIN_SCORE_THRESH = 0.5
MAX_BOXES_TO_DRAW = 5
MIN_TEST_TIME = 2  # the time take to detect the weapon in seconds

INDICAOR_MESSAGES = json.loads(
    open(os.path.join("Configs", "INDICATOR_MESSAGES.json")).read()
)


#    _____ ____  __  __ __  __
#   / ____/ __ \|  \/  |  \/  |
#  | |   | |  | | \  / | \  / |
#  | |   | |  | | |\/| | |\/| |
#  | |___| |__| | |  | | |  | |
#   \_____\____/|_|  |_|_|  |_|


def communication():
    global frame_bytes, frame, is_cap_open, SERVER_ADDRESS, confident
    # s = ClientSocket()
    # client_encryption = RSAEncyption()
    # client_encryption.generate_keys()

    # ##########key exchange#############
    # s.send_buffered(
    #     Message(client_encryption.export_my_pubkey()), SERVER_ADDRESS)
    # m, _ = s.recv()
    # client_encryption.load_others_pubkey(m.get_plain_msg())

    # print(f"client pubkey: {hashlib.sha256(client_encryption.export_my_pubkey()).hexdigest()}", type(
    #     client_encryption.export_my_pubkey()))
    # print(f"server pubkey: {hashlib.sha256(client_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(
    #     client_encryption.other_pubkey.save_pkcs1()))
    # ############################
    # while frame is None:
    #     sleep(.07)
    # print("sending image")
    # # cv2.imwrite("tmp.png", frame, [cv2.IMWRITE_PNG_COMPRESSION, 8])
    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg", "rb") as f:
    #     m = Message(f.read()*10)
    # s.send_buffered(m, SERVER_ADDRESS)
    # # s.send_buffered(Message(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY).tobytes()), SERVER_ADDRESS)
    # print("done")

    client_socket = ClientSocket("TCP")
    client_socket.connect(SERVER_ADDRESS)
    print("connected to server")

    client_rsa = RSAEncyption()
    client_rsa.generate_keys()

    client_socket.send_buffered(
        Message(client_rsa.export_my_pubkey(), code=CommunicationCode.KEY))
    m = client_socket.recv()
    client_rsa.load_others_pubkey(m.get_plain_msg())

    print(
        f"client pubkey: {hashlib.sha256(client_rsa.export_my_pubkey()).hexdigest()}")
    print(
        f"server pubkey: {hashlib.sha256(client_rsa.other_pubkey.save_pkcs1()).hexdigest()}")

    client_aes = AESEncryption()
    client_socket.send_buffered(
        Message(client_aes.key, code=CommunicationCode.KEY), e=client_rsa)
    print(f"AES key: {hashlib.sha256(client_aes.key).hexdigest()}")

    client_socket.send(
        Message(pickle.dumps((ClientSocket.WIDTH_WEBCAM, ClientSocket.HEIGHT_WEBCAM)), code=CommunicationCode.INFO),
        e=client_aes
    )
    sent_message = False# sent a message indicating that a weapon has been found
    while frame is None:
        sleep(.07)
    while is_cap_open:
        mutex = threading.Lock()
        mutex.acquire()
        print(confident)
        if confident:
            if not sent_message:
                m = Message("found", code=CommunicationCode.INFO)
                print(m)
                client_socket.send(m, e=client_aes)
                # client_socket.send(m)

        else:
            sent_message = False
        mutex.release()
        
        # m = Message(pickle.dumps(frame))
        m = Message(frame.tobytes())
        try:
            # client_socket.send_buffered(m)
            # client_socket.send_buffered(m, e=client_rsa)
            client_socket.send_buffered(m, e=client_aes)
        except (ConnectionResetError, ConnectionAbortedError):
            print("server is closed")
            break

        # sig = Message(client_rsa.generate_signature(m.message))
        # client_socket.send_buffered(sig, e=client_rsa)

    client_socket.close()


#   _____ _   _ _____ _______       _      _____ ____________   __  __  ____  _____  ______ _
#  |_   _| \ | |_   _|__   __|/\   | |    |_   _|___  /  ____| |  \/  |/ __ \|  __ \|  ____| |
#    | | |  \| | | |    | |  /  \  | |      | |    / /| |__    | \  / | |  | | |  | | |__  | |
#    | | | . ` | | |    | | / /\ \ | |      | |   / / |  __|   | |\/| | |  | | |  | |  __| | |
#   _| |_| |\  |_| |_   | |/ ____ \| |____ _| |_ / /__| |____  | |  | | |__| | |__| | |____| |____
#  |_____|_| \_|_____|  |_/_/    \_\______|_____/_____|______| |_|  |_|\____/|_____/|______|______|


def initialize_model(done_loading_flag) -> None:
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


def detection_interface(frame) -> tuple:
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


def gui(detection_mode=True) -> None:
    """
    this function is responsible for the GUI of the program.
    :param detection_mode: True if the detection mode is enabled, False otherwise.
    :type detection_mode: bool
    """
    global WIDTH_WEBCAM, HEIGHT_WEBCAM, MIN_SCORE_THRESH, MIN_TEST_TIME, frame_bytes, frame, is_cap_open, confident

    layout, w, h = generate_detection_gui_client()

    cap = cv2.VideoCapture(0)
    window = sg.Window('SmartSec Client', layout, size=(w, h))

    t0_exists = False
    confident = False

    # EVENT LOOP
    is_cap_open = True
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
                mutex = threading.Lock()
                mutex.acquire()
                if not t0_exists:
                    t0 = Timer()
                    confident = False
                else:
                    if t0.elapsed_time() > MIN_TEST_TIME:
                        confident = True
                mutex.release()
            elif t0_exists:
                del t0
                t0_exists = False
                window.refresh()
            gui_weapon_indicator(window, detections, confident)
        mutex = threading.Lock()
        mutex.acquire()
        frame_bytes = cv2.imencode(".png", frame)[1].tobytes()
        mutex.release()
        window["-VIDEO-"].update(data=frame_bytes)

    is_cap_open = False
    cap.release()
    window.close()


#   __  __          _____ _   _
#  |  \/  |   /\   |_   _| \ | |
#  | \  / |  /  \    | | |  \| |
#  | |\/| | / /\ \   | | | . ` |
#  | |  | |/ ____ \ _| |_| |\  |
#  |_|  |_/_/    \_\_____|_| \_|
def main(detection_mode=True) -> None:
    """
    this function is responsible for the main execution of the program - integrating between all of the necassary functions.
    """
    event = show_welcome_client()

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
        if event == "-CONNECT-SERVER-BUTTON-":
            comm_thread = threading.Thread(target=communication, daemon=True)
            comm_thread.start()
        gui(detection_mode)
        # gui(False)
        comm_thread.join() if "comm_thread" in locals() else None


if __name__ == "__main__":
    main()
