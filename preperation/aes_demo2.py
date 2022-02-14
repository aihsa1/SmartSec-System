from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import scrypt
import os
import io

key = os.urandom(32)
# plaintext = "hello world!".encode()
# file_object = io.BytesIO(plaintext)

a = AES.new(key, AES.MODE_GCM)
b = AES.new(key, AES.MODE_GCM, a.nonce)
print(a.nonce)
print(b.nonce)