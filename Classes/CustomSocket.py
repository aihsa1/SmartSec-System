import socket
from Message import Message


class ClientSocket:
    def __init__(self, dst, protocol="UDP") -> None:
        self.dst = dst
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM if protocol == "UDP" else socket.SOCK_STREAM)
        self.protocol = protocol

    def send(self, m: Message) -> None:
        self.socket.sendto(m.__str__().encode(), self.dst)

    def send_buffered(self, m: Message) -> None:
        for start, end in m.splitted_data_generator(100):
            self.socket.sendto(m.message[start: end], self.dst)
    
    def close(self) -> None:
        self.socket.close() if self.protocol == "TCP" else None


def main():
    s = ClientSocket(("127.0.0.1", 14_000))
    m = Message("Hello World!")
    with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg", "rb") as f:
        m = Message(f.read())
        s.send_buffered(m)


if __name__ == "__main__":
    main()
