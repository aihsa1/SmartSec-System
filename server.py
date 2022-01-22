import socket
from Classes.Message import Message

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 14_000))

new_msg = True
while True:
    data, address = s.recvfrom(1024)
    if new_msg:
        m = Message.create_message_from_plain_data(data)
        new_msg = False
    else:
        m += data
    if m.is_complete:
        break
print(m.get_plain_msg())
with open("img.jpg", "wb") as f:
    f.write(m.get_plain_msg())
new_m = Message("Hello Client")
s.sendto(new_m.__str__().encode(), address)
