import os
import sys

CLASSES_FOLDER_PATH = os.path.join(os.getcwd(), "Classes")
SCREENS_FOLDER_PATH = os.path.join(os.getcwd(), "Screens")
SCRIPTS_FOLDER_PATH = os.path.join(os.getcwd(), "Scripts")

for p in (CLASSES_FOLDER_PATH, SCREENS_FOLDER_PATH, SCRIPTS_FOLDER_PATH):
    sys.path.append(p)
# print("\n".join(sorted(sys.path)))
