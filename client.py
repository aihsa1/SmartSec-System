import PySimpleGUI as sg
import tensorflow as tf
import numpy as np
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import cv2
import os


model = None
category_index = None
detect_fn = None
paths = None
files = None
labels = None


def communication():
    pass

###############################################################################

####################DETECTION PROCCEDURE####################


def initialize_model():
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


def detection_interface(frame):
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
        max_boxes_to_draw=5,
        min_score_thresh=0.5,
        agnostic_mode=False)
    return frame_np_with_detections

####################GUI####################


def gui():
    # GUI INITIALIZATION
    cap = cv2.VideoCapture(0)
    WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    w, h = int(WIDTH_WEBCAM * 1.3), int(HEIGHT_WEBCAM * 1.3)

    layout = [
        [sg.Text("Webcam Feed With Detections", justification="center")],
        [sg.Image(key="-VIDEO-", size=(WIDTH_WEBCAM, HEIGHT_WEBCAM), pad=(((w - WIDTH_WEBCAM)
                  * 0.5, (h - HEIGHT_WEBCAM) * 0.5, (0, 0))))],
        [sg.VSeparator()]
    ]

    cap = cv2.VideoCapture(0)
    window = sg.Window('SmartSec Client', layout, size=(w, h))

    # EVENT LOOP
    while True:
        ret, frame = cap.read()
        event, value = window.read()

        window["-VIDEO-"].update(data=(cv2.imencode(".png", frame)[1].tobytes()))

        if event == sg.WIN_CLOSED:
            break

    cap.release()
    window.close()

###############################################################################


def main():
    # initialize_model()
    gui()


if __name__ == "__main__":
    main()
