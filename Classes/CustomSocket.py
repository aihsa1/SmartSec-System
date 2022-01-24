
import socket

from grpc import server
from Message import Message
from RSAEncryption import RSAEncyption


class ClientSocket:
    """
    This class is responsible for creating and manipulating a client socket.
    All of the functions and properties were organized in purpose of making the communication easier to use in this project.
    NOTE: This class is not responsible for the connection between the client and the server, it only creates the socket and makes it ready to be used. Also, this class is a base class for the ServerSocket class.
    """

    def __init__(self, protocol: str = "UDP", existing_socket=None) -> None:
        """
        This function is responsible for creating a client socket.
        :param protocol: The protocol to use.
        :type protocol: str("TCP", "UDP")
        """
        if existing_socket is None:
            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM if protocol == "UDP" else socket.SOCK_STREAM
        )
        else:
            self.socket = existing_socket
        self.protocol = protocol

    @classmethod
    def create_client_socket(cls, client_socket) -> "ClientSocket":
        """
        This function is a factory method for ClientSocket from existing socket object.
        :return: The client socket object.
        :rtype: ClientSocket
        """
        return cls("TCP", client_socket)

    def connect(self, addr) -> None:
        """
        This function is responsible for connecting to the server. USE ONLY FOR TCP
        :param addr: The address of the server to connect.
        :type addr: tuple(ip, port)
        """
        if self.protocol == "UDP":
            raise ValueError("UDP communication does not require connection.")
        else:
            self.socket.connect(addr)

    def send(self, m: Message, addr: tuple = None) -> None:
        """
        This function is responsible for sending a message to the server. It should be NOTED that this function is not responsible for sending data buffered - the data is sent as one chunk. Use send_buffered method in order to do that.
        :param m: The message to send.
        :type m: Message
        :param addr: The address of the server to connect.
        :type addr: tuple(ip, port)
        """
        if self.protocol == "UDP":
            send_cmd = lambda x: self.socket.sendto(x, addr)
        else:
            if addr is None:
                send_cmd = lambda x: self.socket.send(x)
            else:
                raise ValueError(
                    "No need to specify address. It is required for UDP communication, not TCP.")
        if isinstance(m.message, str):
            send_cmd(m.message.encode())
        else:
            send_cmd(m.message)

    def send_buffered(self, m: Message, addr: tuple = None, batch_size: int = 1000) -> None:
        """
        This function is responsible for BUFFERING AND SENDING message to the server.
        :param m: The message to send.
        :type m: Message
        :param addr: The address of the server to connect. This param will be ignored for TCP communication.
        :type addr: tuple(ip, port)
        :param batch_size: The size of the batch.
        :type batch_size: int
        """
        if self.protocol == "UDP":
            send_cmd = lambda x: self.socket.sendto(x, addr)
        else:
            if addr is None:
                send_cmd = lambda x: self.socket.send(x)
            else:
                raise ValueError(
                    "No need to specify address. It is required for UDP communication, not TCP.")
        
        if isinstance(m.message, str):
            for start, end in m.splitted_data_generator(batch_size):
                send_cmd(m.message[start: end].encode())
        else:
            for start, end in m.splitted_data_generator(batch_size):
                send_cmd(m.message[start: end])

    def recv(self, buffer_size: int = 1024) -> Message:
        """
        This function is responsible for receiving a message from the server. This function takes buffered data into account. The recieved data is returned as a Message object.
        :param buffer_size: The size of the buffer.
        :type buffer_size: int
        :return: The message received and the origin.
        :rtype: tuple(Message, tuple(ip, port))
        """
        new_msg = True
        if self.protocol == "UDP":
            recv_cmd = self.socket.recvfrom
            while True:
                data, address = recv_cmd(buffer_size)
                if new_msg:
                    m = Message.create_message_from_plain_data(data)
                    new_msg = False
                else:
                    m += data
                if m.is_complete:
                    return m, address
        else:
           recv_cmd = self.socket.recv
           while True:
                data = recv_cmd(buffer_size)
                if new_msg:
                    m = Message.create_message_from_plain_data(data)
                    new_msg = False
                else:
                    m += data
                if m.is_complete:
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
        This function is responsible for creating a server socket. It should be NOTED that this function is not responsible for binding the socket, only for creating the socket object -  use the bind_and_listen method should be used in order to do the binding.
        :param protocol: The protocol to use.
        :type protocol: str("TCP", "UDP")
        """
        super().__init__(protocol=protocol)
        self.is_bound = False

    def bind_and_listen(self, addr: tuple):
        """
        This function is responsible for binding the server socket to a certain address and port and listen (if this is a TCP socket).
        :param addr: The address to bind to.
        :type addr: tuple(ip, port)
        """
        self.socket.bind(addr)
        self.socket.listen() if self.protocol == "TCP" else None
    
    def accept(self):
        if self.protocol == "UDP":
            raise ValueError("UDP communication does not require connection.")
        else:
            return self.socket.accept()

    def getpeername(self):
        """
        This function is responsible for getting the address of the client that is connected to the server (ONLY ON TCP).
        :return: The address of the client that is connected to the server.
        :rtype: tuple(ip, port)
        """
        return self.socket.getpeername() if self.protocol == "TCP" else None


def main():

    SERVER_ADDRESS = ("127.0.0.1", 14_000)
    s = ClientSocket()
    client_encryption = RSAEncyption()
    client_encryption.generate_keys()
    ##########key exchange##########
    s.send_buffered(Message(client_encryption.my_pubkey))
    server_pubkey = s.recv(); client_encryption.other_pubkey = server_pubkey
    print(f"my pubkey: {client_encryption.my_pubkey}")
    print(f"other's pubkey: {client_encryption.other_pubkey}")
    ##########end exchange##########

    m = Message(b"Hello World!")
    with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg", "rb") as f:
        m = Message(f.read())
    s.send_buffered(m, SERVER_ADDRESS)
    m, addr = s.recv()
    print(m)

    # SERVER_ADDRESS = ("127.0.0.1", 14_000)
    # s = ClientSocket("TCP")
    # s.connect(SERVER_ADDRESS)
    # # m = Message(b"Hello World!")
    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg", "rb") as f:
    #     m = Message(f.read())
    # s.send_buffered(m)
    # m = s.recv()
    # print(m)


if __name__ == "__main__":
    main()
