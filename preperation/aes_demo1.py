from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

key = os.urandom(16)
"""
1
"""
#############key exchange#############
cipher = AES.new(key, AES.MODE_CBC)

plaintext = b"hello world"*1000

ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
iv = cipher.iv
print(ciphertext)
##send data

cipher = AES.new(key, AES.MODE_CBC, iv)

plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
print(plaintext.decode())

####################################################################
####################################################################

cipher = AES.new(key, AES.MODE_CBC)
iv = cipher.iv
plaintext = b"how are you"*1000

ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
####################################################################

cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
print(plaintext.decode())
