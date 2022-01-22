import socket
from Message import Message


class ClientSocket:
    """
    This class is responsible for creating and manipulating a client socket.
    All of the functions and properties were organized in purpose of making the communication easier to use in this project.
    NOTE: This class is not responsible for the connection between the client and the server, it only creates the socket and makes it ready to be used. Also, this class is a base class for the ServerSocket class.
    """

    def __init__(self, addr: tuple = None, protocol: str = "UDP") -> None:
        """
        This function is responsible for creating a client socket.
        :param addr: The address of the server to connect.
        :type addr: tuple(ip, port)
        :param protocol: The protocol to use.
        :type protocol: str("TCP", "UDP")
        """
        self.addr = addr
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM if protocol == "UDP" else socket.SOCK_STREAM)
        self.protocol = protocol

    def send(self, m: Message) -> None:
        """
        This function is responsible for sending a message to the server. It should be NOTED that this function is not responsible for sending data buffered - the data is sent as one chunk. Use send_buffered method in order to do that.
        :param m: The message to send.
        :type m: Message
        """
        if self.addr is None:
            raise Exception("No address specified")
        self.socket.sendto(m.__str__().encode(
        ), self.addr) if self.protocol == "UDP" else self.socket.send(m.__str__().encode())

    def send_buffered(self, m: Message, batch_size: int = 1000) -> None:
        """
        This function is responsible for BUFFERING AND SENDING message to the server.
        :param m: The message to send.
        :type m: Message
        """
        if self.addr is None:
            raise Exception("No address specified")
        if self.protocol == "UDP":
            for start, end in m.splitted_data_generator(batch_size):
                self.socket.sendto(m.message[start: end], self.addr)
        else:
            for start, end in m.splitted_data_generator(batch_size):
                self.socket.send(m.message[start: end])

    def recv(self, buffer_size: int = 1024) -> Message:
        """
        This function is responsible for receiving a message from the server. This function takes buffered data into account. The recieved data is returned as a Message object.
        :param buffer_size: The size of the buffer.
        :type buffer_size: int
        :return: The message received from the server.
        :rtype: Message
        """
        new_msg = True
        recv_cmd = self.socket.recvfrom if self.protocol == "UDP" else self.socket.recv
        while True:
            data, address = recv_cmd(buffer_size)
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
    """
    This class is responsible for creating and manipulating a server socket.
    All of the functions and properties were organized in purpose of making the communication easier to use in this project.
    NOTE: this class inherits from ClientSocket class and therefore all of the functions and properties are available with some small modifications (polymorphism). This Class consists additional methods for server-use only.
    """

    def __init__(self, protocol: str = "UDP") -> None:
        """
        This function is responsible for creating a server socket. It should be NOTED that this function is not responsible for binding the socket, only for creating the socket object -  use the bind method should be used in order to do the binding.
        :param protocol: The protocol to use.
        :type protocol: str("TCP", "UDP")
        """
        super().__init__(protocol=protocol)
        self.is_bound = False

    def bind(self, addr: tuple):
        """
        This function is responsible for binding the server socket to a certain address and port.
        :param addr: The address to bind to.
        :type addr: tuple(ip, port)
        """
        self.socket.bind(addr)
        self.is_bound = True

    def getpeername(self):
        """
        This function is responsible for getting the address of the client that is connected to the server.
        :return: The address of the client that is connected to the server.
        :rtype: tuple(ip, port)
        """
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
