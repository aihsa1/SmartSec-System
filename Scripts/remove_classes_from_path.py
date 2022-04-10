import os
import sys

CLASSES_FOLDER_PATH = os.path.join(os.getcwd(), "Classes")
if CLASSES_FOLDER_PATH in sys.path:
    sys.path.remove(CLASSES_FOLDER_PATH)
print(sys.path)
