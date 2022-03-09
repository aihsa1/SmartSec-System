import base64
import sys
import os


img_name = sys.argv[1]
with open(os.path.join(os.getcwd(), img_name), "rb") as f:
    img_encoded = base64.b64encode(f.read())
    print(type(img_encoded))
with open(os.path.join(os.getcwd(), img_name + "ENCODED.txt"), "wb") as f:
    f.write(img_encoded)