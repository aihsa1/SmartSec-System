import cv2

img = cv2.imread("img92.jpg")

succes_flag, img = cv2.imencode(".png", img)
print(img.tobytes())