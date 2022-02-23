import cv2
import PySimpleGUI as sg


def generate_detection_gui_layout():

    # N_CAMERAS = 2

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
                        sg.Button(button_text="<", key="-BUTTON-NEXT-",
                                  enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005))),
                        sg.Button(button_text=">", key="-BUTTON-PREV-",
                                  enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005)))
                    ],
                    [
                        sg.Image(filename='', key="-VIDEO-", enable_events=True, size=(WIDTH_WEBCAM, HEIGHT_WEBCAM), pad=(
                            ((w - WIDTH_WEBCAM) * 0.5, (h - HEIGHT_WEBCAM) * 0.5, (0, 0))), background_color="black", tooltip=f"Cam 1"),
                    ]
                ], element_justification="center")
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
        # if event == "-BUTTON-NEXT-":
        #     i += 1
        # if event == "-BUTTON-PREV-":
        #     i -= 1

    window.close()
