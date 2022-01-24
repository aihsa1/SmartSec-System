
import sys
import os
import hashlib
CLASSES_FOLDER_PATH = os.path.join(os.getcwd(), "Classes")
if CLASSES_FOLDER_PATH not in sys.path:
    sys.path.append(CLASSES_FOLDER_PATH)
from Classes.Message import Message
from Classes.RSAEncryption import RSAEncyption
from Classes.CustomSocket import ServerSocket, ClientSocket
sys.path.remove(CLASSES_FOLDER_PATH)

###############################UDP#####################################################
# s = ServerSocket()
# s.bind_and_listen(("127.0.0.1", 14_000))
# server_encryption = RSAEncyption()
# server_encryption.generate_keys()

# ########key exchange#########
# m, addr = s.recv()
# server_encryption.load_others_pubkey(m.get_plain_msg())
# s.send_buffered(Message(server_encryption.export_my_pubkey()), addr)
# ##########################

# m, addr = s.recv(e=server_encryption)
# sig, _ = s.recv(e=server_encryption)
# print(server_encryption.verify_signature(m.message, sig.get_plain_msg()))

# with open("img.jpg", "wb") as f:
#     f.write(m.get_plain_msg())

# new_m = Message("Hi")
# s.send(new_m, addr, e=server_encryption)
############################TCP###################################
server_socket = ServerSocket("TCP")
server_socket.bind_and_listen(("127.0.0.1", 14_000))
client, client_addr = server_socket.accept()
client = ClientSocket.create_client_socket(client)

#########key exchange#########
server_encryption = RSAEncyption()
server_encryption.generate_keys()

m = client.recv()
server_encryption.load_others_pubkey(m.get_plain_msg())
client.send_buffered(Message(server_encryption.export_my_pubkey()))

print(f"client pubkey: {hashlib.sha256(server_encryption.other_pubkey.save_pkcs1()).hexdigest()}")
print(f"server pubkey: {hashlib.sha256(server_encryption.export_my_pubkey()).hexdigest()}")
##############################

m = client.recv(e=server_encryption)
with open("img.jpg", "wb") as f:
    f.write(m.get_plain_msg())
new_m = Message("Hello Client")
client.send(new_m, e=server_encryption)

