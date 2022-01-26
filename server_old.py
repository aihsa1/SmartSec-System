
import hashlib
import sys
import os
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
# print("incomig image")
# m, addr = s.recv(e=server_encryption)
# sig, _ = s.recv(e=server_encryption)
# print(server_encryption.verify_signature(m.message, sig.get_plain_msg()))

# with open("img.jpg", "wb") as f:
#     f.write(m.get_plain_msg())

# new_m = Message("Hi")
# s.send(new_m, addr, e=server_encryption)
############################TCP###################################
# server_socket = ServerSocket("TCP")
# server_socket.bind_and_listen(("127.0.0.1", 14_000))
# client, client_addr = server_socket.accept()
# client = ClientSocket.create_client_socket(client)

# #########key exchange#########
# server_encryption = RSAEncyption()
# server_encryption.generate_keys()

# m = client.recv()
# server_encryption.load_others_pubkey(m.get_plain_msg())
# client.send_buffered(Message(server_encryption.export_my_pubkey()))

# # print(f"client pubkey: {hashlib.sha256(server_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(server_encryption.other_pubkey.save_pkcs1()))
# # print(f"server pubkey: {hashlib.sha256(server_encryption.export_my_pubkey()).hexdigest()}", type(server_encryption.export_my_pubkey()))

# # print(server_encryption.my_pubkey)
# # print(server_encryption.other_pubkey)
# ##############################

# del m
# m = client.recv(e=server_encryption)
# print(m.message)
# # print(base64.b64decode(m.message))
# with open("img.jpg", "wb") as f:
#     f.write(m.get_plain_msg())
# new_m = Message("Hello Client")
# client.send(new_m, e=server_encryption)

###################TCP2###############################

server_socket = ServerSocket("TCP")
server_socket.bind_and_listen(("0.0.0.0", 14_000))
client_socket, addr = server_socket.accept()
client_socket = ClientSocket.create_client_socket(client_socket)

print("client connencted")
###########key exchange#########
server_encryption = RSAEncyption()
server_encryption.generate_keys()

m = client_socket.recv()
server_encryption.load_others_pubkey(m.get_plain_msg())
client_socket.send_buffered(Message(server_encryption.export_my_pubkey()))

print(f"client pubkey: {hashlib.sha256(server_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(server_encryption.other_pubkey.save_pkcs1()))
print(f"server pubkey: {hashlib.sha256(server_encryption.export_my_pubkey()).hexdigest()}", type(server_encryption.export_my_pubkey()))
###############################################

m = client_socket.recv(e=server_encryption)
print("recieved image")
sig = client_socket.recv(e=server_encryption)
print(server_encryption.verify_signature(m.message, sig.get_plain_msg()))
print("signature recieved")
with open("img.jpg", "wb") as f:
    f.write(m.get_plain_msg())

client_socket.close()
server_socket.close()