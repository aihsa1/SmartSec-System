import hashlib
import sys
import os
from Scripts import add_classes_to_path
from Classes.Message import Message
from Classes.RSAEncryption import RSAEncyption
from Classes.CustomSocket import ServerSocket

s = ServerSocket()
s.bind_and_listen(("0.0.0.0", 14_000))
server_encryption = RSAEncyption()
server_encryption.generate_keys()

########key exchange#########
m, addr = s.recv()
server_encryption.load_others_pubkey(m.get_plain_msg())
s.send_buffered(Message(server_encryption.export_my_pubkey()), addr)

print(f"client pubkey: {hashlib.sha256(server_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(server_encryption.other_pubkey.save_pkcs1()))
print(f"server pubkey: {hashlib.sha256(server_encryption.export_my_pubkey()).hexdigest()}", type(server_encryption.export_my_pubkey()))
##########################