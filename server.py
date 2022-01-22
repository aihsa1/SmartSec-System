
import sys
import os
CLASSES_FOLDER_PATH = os.path.join(os.getcwd(), "Classes")
if CLASSES_FOLDER_PATH not in sys.path:
    sys.path.append(CLASSES_FOLDER_PATH)
from Classes.Message import Message
from Classes.CustomSocket import ServerSocket, ClientSocket
sys.path.remove(CLASSES_FOLDER_PATH)

# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.bind(("127.0.0.1", 14_000))

# new_msg = True
# while True:
#     data, address = s.recvfrom(1024)
#     if new_msg:
#         m = Message.create_message_from_plain_data(data)
#         new_msg = False
#     else:
#         m += data
#     if m.is_complete:
#         break
# print(m.get_plain_msg())
####################################################################################
# s = ServerSocket()
# s.bind_and_listen(("127.0.0.1", 14_000))
# m, addr = s.recv()
# with open("img.jpg", "wb") as f:
#     f.write(m.get_plain_msg())

# new_m = Message("Hello Client")
# s.send(new_m, addr)
###############################################################
server_socket = ServerSocket("TCP")
server_socket.bind_and_listen(("127.0.0.1", 14_000))
client, client_addr = server_socket.accept()
client = ClientSocket.create_client_socket(client)

m = client.recv()
with open("img.jpg", "wb") as f:
    f.write(m.get_plain_msg())
new_m = Message("Hello Client")
client.send(new_m)

