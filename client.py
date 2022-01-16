import PySimpleGUI as sg
import cv2

cap = cv2.VideoCapture(0)
WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

w, h = int(WIDTH_WEBCAM * 1.3), int(HEIGHT_WEBCAM * 1.3)

print(WIDTH_WEBCAM, HEIGHT_WEBCAM)

layout = [
    [sg.Text("Webcam Feed With Detections", justification="center")],
    [sg.Image(key="-VIDEO-", size=(WIDTH_WEBCAM, HEIGHT_WEBCAM), pad=(((w - WIDTH_WEBCAM) * 0.5, (h -HEIGHT_WEBCAM) * 0.5, (0, 0))), background_color="black")],
    [sg.VSeparator()]
]

window = sg.Window('SmartSec Client', layout, size=(w, h))

while True:
    event, value = window.read()
    if event == sg.WIN_CLOSED:
        break
window.close()