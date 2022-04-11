import cv2
import os
import json
import PySimpleGUI as sg


N_CAMERAS = 10

N_IN_ROWS = 2
N_CAMERAS_IN_PAGE = 4


def generate_detection_gui_client():

    with open(os.path.join("Configs", "dimensions.json"), "r") as f:
        WIDTH_WEBCAM, HEIGHT_WEBCAM = json.load(f).values()

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

    with open(os.path.join("Configs", "dimensions.json"), "r") as f:
        WIDTH_WEBCAM, HEIGHT_WEBCAM = json.load(f).values()

    w, h = int(WIDTH_WEBCAM * 1.2), int(HEIGHT_WEBCAM * 1.2)
    with open(os.path.join("Configs", "icons.json"), "r") as f:
        DB_IMAGE = json.loads(f.read())["db"]

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
                    [sg.Button(button_text="", key="-DB-BUTTON-", image_data=DB_IMAGE,
                               tooltip="open/close mic", focus=False, enable_events=True)]
                ]
        )
        ]
    ]
    return layout, w, h


def generate_db_gui_server(data, headings):
    with open(os.path.join("Configs", "dimensions.json"), "r") as f:
        w, h = json.load(f).values()
    with open(os.path.join("Configs", "icons.json"), "r") as f:
        DB_IMAGE = json.loads(f.read())["back"]

    layout = [
        [
            sg.Column([
                [
                    sg.Text("DB Documents", justification="center",
                            font=(*sg.DEFAULT_FONT, "bold underline"), key="-TITLE-")
                ],
                [
                    sg.Button(button_text="", key="-DB-BUTTON-", image_data=DB_IMAGE,
                              tooltip="open/close mic", focus=False, enable_events=True)
                ],
                [sg.Table(
                    values=data,
                    headings=headings,
                    def_col_width=20,
                    num_rows=50,
                    auto_size_columns=False,
                    expand_x=True,
                    expand_y=True,
                    vertical_scroll_only=True,
                    display_row_numbers=True,
                    justification='right',
                    key="-TABLE-",
                    enable_events=True
                )
                ]
            ], element_justification="c", justification="c", pad=(0, 0, 0, 0))
        ],
    ]
    return layout, w, h


def db_alert_gui_server(output, image):
    sg.popup_no_buttons(output.__str__(), title=f"info",
                        image=sg.EMOJI_BASE64_HAPPY_BIG_SMILE)


def main():
    # i = 0
    # layout, w, h = generate_detection_gui_server()
    # # layout, w, h = generate_detection_gui_client()
    # window = sg.Window('SmartSec Server', layout, size=(w, h))
    # while True:
    #     event, value = window.read(timeout=10)
    #     if event == sg.WIN_CLOSED:
    #         break
    #     # if event == "-BUTTON-NEXT-":
    #     #     for j in range(min(N_CAMERAS_IN_PAGE, N_CAMERAS)):
    #     #         window[f"-VIDEO{i * N_CAMERAS_IN_PAGE + j}-"].Update(visible=False)
    #     #     for j in range(min(N_CAMERAS_IN_PAGE, N_CAMERAS-N_CAMERAS_IN_PAGE)):
    #     #         print(f"{(i + 1) * N_CAMERAS_IN_PAGE + j} is visible")
    #     #         window[f"-VIDEO{(i + 1) * N_CAMERAS_IN_PAGE + j}-"].Update(visible=True)
    #     #     i += 1

    #     # [
    #     # sg.Button(button_text="<", key="-BUTTON-PREV-",
    #     #             enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005))),
    #     # sg.Button(button_text=">", key="-BUTTON-NEXT-",
    #     #             enable_events=True, size=(int(WIDTH_WEBCAM * 0.005), int(HEIGHT_WEBCAM * 0.005)))
    #     # ]

    # window.close()

    # --------------------------------------------------------------------------------------------------------------------

    import bson
    import datetime

    data = [
        {'_id': bson.ObjectId('624089122f3170c6f1338089'),
         'name': 'David', 'age': 3000},
        {'_id': bson.ObjectId('62414e87c1438f8812a2d5fd'),
         'name': 'David', 'age': 3000},
        {'_id': bson.ObjectId('6243e3bd19115361e3eb1422'),
         'name': 'Davidov', 'age': 3000},
        {'_id': bson.ObjectId('624089122f3170c6f133808a'),
         'name': 'Jacob', 'age': 50},
        {'_id': bson.ObjectId('624088f14d260b008081f374'),
         'name': 'Ran Davidos', 'age': 3000}
    ]
    data = [list(v.values()) for v in data]
    # data = [
    #     ['Bob', '24', 'Engineer'],
    #     ['Sue', '40', 'Retired'],
    #     ['Joe', '32', 'Programmer'],
    #     ['Mary', '28', 'Teacher'],
    # ]
    layout, w, h = generate_db_gui_server(data, ["_id", "name", "age"])
    w = sg.Window("SmartSec DB", layout, size=(w, h), resizable=True)
    while True:
        event, values = w.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == '-TABLE-':
            i = values["-TABLE-"][0]
            print(i)
    w.close()


if __name__ == "__main__":
    main()
