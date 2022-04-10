import cv2

cap = cv2.VideoCapture(0)
w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frame_precent = 2
top_bottom_frame_width = int(w * frame_precent / 100)
left_right_frame_width = int(h * frame_precent / 100)

frame_color = (0, 255, 0)

while True:
    _, img = cap.read()
    # img[0, :, :] = frame_color
    # img[-1, :, :] = frame_color
    # img[:, 0, :] = frame_color
    # img[:, -1, :] = frame_color
    img[0: top_bottom_frame_width, :, :] = frame_color
    img[top_bottom_frame_width * (-1):, :, :] = frame_color
    img[:, 0: left_right_frame_width, :] = frame_color
    img[:, left_right_frame_width * (-1):, :] = frame_color
    cv2.imshow('frame', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
