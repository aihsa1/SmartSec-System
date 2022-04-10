import cv2
import os
import json
import PySimpleGUI as sg


N_CAMERAS = 10

N_IN_ROWS = 2
N_CAMERAS_IN_PAGE = 4


def generate_detection_gui_client():

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
        [
            sg.Column(
                [
                    [
                        sg.Image(filename='', key="-VIDEO-", enable_events=True, size=(WIDTH_WEBCAM, HEIGHT_WEBCAM), pad=(
                            ((w - WIDTH_WEBCAM) * 0.5, (h - HEIGHT_WEBCAM) * 0.5, (0, 0))), background_color="black", tooltip=f"Cam 1"),
                    ]
                ], element_justification="center")
        ],
    ]
    return layout, w, h


def generate_detection_gui_server():
    global N_CAMERAS, N_IN_ROWS, N_CAMERAS_IN_PAGE

    with open(os.path.join("Configs", "icons.json"), "r") as f:
        MIC_IMAGE = json.loads(f.read())["mic"]

    cap = cv2.VideoCapture(0)
    WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    w, h = int(WIDTH_WEBCAM * 1.2), int(HEIGHT_WEBCAM * 1.2)

    cameras_layout = []
    image_index = 0
    for _ in range(N_CAMERAS//2):
        row = []
        for _ in range(2):
            row.append(sg.Image(filename='', key=f"-VIDEO{image_index}-", enable_events=True, size=(WIDTH_WEBCAM // 2, HEIGHT_WEBCAM // 2),
                                background_color="black", tooltip=f"Cam {image_index}"))
            image_index += 1
        cameras_layout.append(row)
    if N_CAMERAS % N_IN_ROWS == 1:
        cameras_layout.append([sg.Image(filename='', key=f"-VIDEO{image_index}-", enable_events=True, size=(
            WIDTH_WEBCAM // 2, HEIGHT_WEBCAM // 2), background_color="black", tooltip=f"Cam {image_index}")])

    layout = [
        [sg.Column(
            [
                [sg.Text("Webcam Feed With Detections", justification="center",
                         font=(*sg.DEFAULT_FONT, "bold underline"), key="-HEADING-")],
                *cameras_layout
            ], scrollable=True, expand_x=True, expand_y=True, element_justification="c"),

            sg.Column(
                [
                    [sg.Button(button_text="", key="-MIC-BUTTON-", image_data=MIC_IMAGE,
                               tooltip="open/close mic", focus=False, enable_events=True)]
                ]
        )
        ]
    ]
    return layout, w, h


if __name__ == "__main__":
    i = 0
    layout, w, h = generate_detection_gui_server()
    # layout, w, h = generate_detection_gui_client()
    window = sg.Window('SmartSec Server', layout, size=(w, h))
    while True:
        event, value = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break
        # if event == "-BUTTON-NEXT-":
        #     for j in range(min(N_CAMERAS_IN_PAGE, N_CAMERAS)):
        #         window[f"-VIDEO{i * N_CAMERAS_IN_PAGE + j}-"].Update(visible=False)
        #     for j in range(min(N_CAMERAS_IN_PAGE, N_CAMERAS-N_CAMERAS_IN_PAGE)):
        #         print(f"{(i + 1) * N_CAMERAS_IN_PAGE + j} is visible")
        #         window[f"-VIDEO{(i + 1) * N_CAMERAS_IN_PAGE + j}-"].Update(visible=True)
        #     i += 1

        # [
        # sg.Button(button_text="<", key="-BUTTON-PREV-",
        #             enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005))),
        # sg.Button(button_text=">", key="-BUTTON-NEXT-",
        #             enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005)))
        # ]

    window.close()
