import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(("127.0.0.1", 14_000))
data , address = s.recvfrom(1024)
print(data.decode())
s.sendto("Hello!".encode(), address)