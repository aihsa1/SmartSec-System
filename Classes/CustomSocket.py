import socket
from Message import Message


class ClientSocket:
    def __init__(self, addr=None, protocol="UDP") -> None:
        self.addr = addr
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM if protocol == "UDP" else socket.SOCK_STREAM)
        self.protocol = protocol

    def send(self, m: Message) -> None:
        if self.addr is None:
            raise Exception("No address specified")

        self.socket.sendto(m.__str__().encode(), self.addr)

    def send_buffered(self, m: Message) -> None:
        if self.addr is None:
            raise Exception("No address specified")

        for start, end in m.splitted_data_generator(100):
            self.socket.sendto(m.message[start: end], self.addr)

    def recv(self, buffer_size: int = 1024) -> Message:
        new_msg = True
        while True:
            data, address = self.socket.recvfrom(buffer_size)
            if new_msg:
                m = Message.create_message_from_plain_data(data)
                new_msg = False
            else:
                m += data
            if m.is_complete:
                break
        return m

    def close(self) -> None:
        self.socket.close() if self.protocol == "TCP" else None


class ServerSocket(ClientSocket):

    def __init__(self, protocol="UDP") -> None:
        super().__init__(protocol=protocol)
        self.is_bound = False

    def bind(self, addr):
        self.socket.bind(addr)
        self.is_bound = True

    def getpeername(self):
        return self.socket.getpeername()


def main():
    s = ClientSocket(("127.0.0.1", 14_000))
    m = Message("Hello World!")
    with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg", "rb") as f:
        m = Message(f.read())
        s.send_buffered(m)
        m = s.recv()
        print(m)


if __name__ == "__main__":
    main()
