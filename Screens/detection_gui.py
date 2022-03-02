import cv2
import PySimpleGUI as sg


def generate_detection_gui_layout():

    N_CAMERAS = 4
    N_IN_ROWS = 2

    cap = cv2.VideoCapture(0)
    WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    w, h = int(WIDTH_WEBCAM * 1.3), int(HEIGHT_WEBCAM * 1.3)

    cameras_layout = []
    for i in range(N_CAMERAS//2):
        row = []
        for j in range(2):
            row.append(sg.Image(filename='', key=f"-VIDEO{i * N_IN_ROWS + j}-", enable_events=True, size=(WIDTH_WEBCAM // N_IN_ROWS, HEIGHT_WEBCAM // N_IN_ROWS), background_color="black", tooltip=f"Cam {i * N_IN_ROWS + j}"))
        cameras_layout.append(row)
    if N_CAMERAS % N_IN_ROWS == 1:
        cameras_layout.append(sg.Image(filename='', key=f"-VIDEO{N_CAMERAS}-", enable_events=True, size=(WIDTH_WEBCAM // N_IN_ROWS, HEIGHT_WEBCAM // N_IN_ROWS), background_color="black", tooltip=f"Cam {N_CAMERAS}"))


    layout = [
        [sg.Text("Webcam Feed With Detections", justification="center",
                 font=(*sg.DEFAULT_FONT, "bold underline"), key="-TITLE-")],
        [sg.Text("Weapon Not Found", justification="left",
                 key="-FOUND-INDICATOR-")],
        [
            [
                        sg.Button(button_text="<", key="-BUTTON-NEXT-",
                                  enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005))),
                        sg.Button(button_text=">", key="-BUTTON-PREV-",
                                  enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005)))
            ],
            cameras_layout
        ],
        [sg.VSeparator()],
    ]
    return layout, w, h


if __name__ == "__main__":
    i = 1
    layout, w, h = generate_detection_gui_layout()
    window = sg.Window('SmartSec Server', layout, size=(w, h))
    while True:
        event, value = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break

    window.close()
