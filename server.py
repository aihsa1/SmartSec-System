import sys
import os
CLASSES_FOLDER_PATH = os.path.join(os.getcwd(), "Classes")
if CLASSES_FOLDER_PATH not in sys.path:
    sys.path.append(CLASSES_FOLDER_PATH)
from Classes.Message import Message
from Classes.RSAEncryption import RSAEncyption
from Classes.CustomSocket import ServerSocket, ClientSocket
sys.path.remove(CLASSES_FOLDER_PATH)

