import hashlib
import socket
import cv2
from Message import Message
from CommunicationCode import CommunicationCode
from RSAEncryption import RSAEncyption
from AESEncryption import AESEncryption
RECV_BUFFER_SIZE = RSAEncyption.RECV_BUFFER_SIZE
RECV_BUFFER_SIZE = 16_384

#TODO PROTOCOL IMPLEMENTATION
class ClientSocket:
    """
    This class is responsible for creating and manipulating a client socket.
    All of the functions and properties were organized in purpose of making the communication easier to use in this project.
    NOTE: This class is not responsible for the connection between the client and the server, it only creates the socket and makes it ready to be used. Also, this class is a base class for the ServerSocket class.
    """

    cap = cv2.VideoCapture(0)
    WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    del cap

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

    def send(self, m: Message, addr: tuple = None, e: RSAEncyption = None, code=CommunicationCode.VIDEO) -> None:
        """
        This function is responsible for sending a message to the server. It should be NOTED that this function is not responsible for sending data buffered - the data is sent as one chunk. Use send_buffered method in order to do that.
        :param m: The message to send.
        :type m: Message
        :param addr: The address of the server to connect.
        :type addr: tuple(ip, port)
        :param e: The encryption object. This param will be used to encrypt messages. if None, no encryption will be used.
        :type e: RSAEncyption
        """
        if self.protocol == "UDP":
            send_cmd = lambda x: self.socket.sendto(x, addr)
        else:
            if addr is None:
                send_cmd = lambda x: self.socket.send(x)
            else:
                raise ValueError(
                    "No need to specify address. It is required for UDP communication, not TCP.")
        if e is not None:
            encrypt_cmd = lambda x: e.encrypt(x)
        else:
            encrypt_cmd = lambda x: x
        
        if isinstance(m.message, str):
            send_cmd(encrypt_cmd(m.message.encode()))
        else:
            send_cmd(encrypt_cmd(m.message))

    def send_buffered(self, m: Message, addr: tuple = None, batch_size: int = RECV_BUFFER_SIZE, e: RSAEncyption = None, code=CommunicationCode.VIDEO) -> None:
        """
        This function is responsible for BUFFERING AND SENDING message to the server.
        :param m: The message to send.
        :type m: Message
        :param addr: The address of the server to connect. This param will be ignored for TCP communication.
        :type addr: tuple(ip, port)
        :param batch_size: The size of the batch. It should be less than rsa.common.byte_size(publickey.n)
        :type batch_size: int
        :param e: The encryption object. This param will be used to encrypt messages. if None, no encryption will be used.
        :type e: RSAEncyption

        """
        if isinstance(e, RSAEncyption):
            batch_size -= 11
        else:
            batch_size -= AESEncryption.KEY_SIZE
        
        if self.protocol == "UDP":
            send_cmd = lambda x: self.socket.sendto(x, addr)
        else:
            if addr is None:
                send_cmd = lambda x: self.socket.send(x)
            else:
                raise ValueError(
                    "No need to specify address. It is required for UDP communication, not TCP.")
        if e is not None:
            encrypt_cmd = lambda x: e.encrypt(x)
        else:
            encrypt_cmd = lambda x: x
        
        
        summary = 0
        if isinstance(m.message, str):
            m = Message(encrypt_cmd(m.get_plain_msg().encode()), code=m.code)
        else:
            m = Message(encrypt_cmd(m.get_plain_msg()), code=m.code.decode())
        for start, end in m.splitted_data_generator(batch_size):
                b = m.message[start: end]
                send_cmd(b)
                summary += end - start
                print(f"{summary/1_000_000} MB sent.")
        print("done")

    def recv(self, buffer_size: int = RECV_BUFFER_SIZE, e: RSAEncyption = None) -> Message:
        """
        This function is responsible for receiving a message from the server. This function takes buffered data into account. The recieved data is returned as a Message object.
        :param buffer_size: The size of the buffer. It should be exactly the same as rsa.common.byte_size(publickey.n)
        :type buffer_size: int
        :return: The message received and the origin.
        :rtype: tuple(Message, tuple(ip, port))
        """
        if e is not None:
            decrypt_cmd = lambda x: e.decrypt(x)
            offset = AESEncryption.KEY_SIZE
        else:
            decrypt_cmd = lambda x: x
            offset = 0
        
        new_msg = True
        if self.protocol == "UDP":
            recv_cmd = self.socket.recvfrom
            while True:
                data, address = recv_cmd(m.message_size - len(m.get_plain_msg()) + offset) if "m" in locals() and m.message_size - len(m.get_plain_msg()) < buffer_size else recv_cmd(buffer_size)
                if new_msg:
                    m = Message.create_message_from_plain_data(data)
                    new_msg = False
                else:
                    m += data
                print(f"{len(m.get_plain_msg())/1_000_000} MB received.")
                if m.is_complete:
                    return Message(decrypt_cmd(m.get_plain_msg())), address
        else:
           recv_cmd = self.socket.recv
           while True:
                # data = recv_cmd(m.message_size - len(m.get_plain_msg())) if "m" in locals() and m.message_size - len(m.get_plain_msg()) < buffer_size else recv_cmd(buffer_size)
                if not new_msg and m.message_size - len(m.get_plain_msg()) + offset < buffer_size:
                    data = recv_cmd(m.message_size - len(m.get_plain_msg()) + offset)
                else:
                    data = recv_cmd(buffer_size)
                if new_msg:
                    m = Message.create_message_from_plain_data(data)
                    new_msg = False
                else:
                    m += data
                print(f"{len(m.get_plain_msg())/1_000_000} MB received.")
                if m.is_complete:
                    return Message(decrypt_cmd(m.get_plain_msg()))
        
        

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
    # s = ClientSocket()
    # client_encryption = RSAEncyption()
    # client_encryption.generate_keys()

    # ##########key exchange#############
    # s.send_buffered(Message(client_encryption.export_my_pubkey()), SERVER_ADDRESS)
    # m, _ = s.recv()
    # client_encryption.load_others_pubkey(m.get_plain_msg())
    # print(f"client pukey: {hashlib.sha256(client_encryption.export_my_pubkey()).hexdigest()}")
    # print(f"server pukey: {hashlib.sha256(client_encryption.other_pubkey.save_pkcs1()).hexdigest()}")
    # ############################
    
    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\publications_2017_nohagim_aheret_nohagim_nachon.pdf", "rb") as f:
    #     m = Message(f.read())
    # s.send_buffered(m, SERVER_ADDRESS)
    # sig = Message(client_encryption.generate_signature(m.message))
    # s.send_buffered(sig, SERVER_ADDRESS, e=client_encryption)


    # m, addr = s.recv(e=client_encryption)
    # print(m.get_plain_msg())

    ####################TCP##############################
    # SERVER_ADDRESS = ("127.0.0.1", 14_000)
    # s = ClientSocket("TCP")
    # s.connect(SERVER_ADDRESS)


    # ##########key exchange#############
    # client_encryption = RSAEncyption()
    # client_encryption.generate_keys()

    # s.send_buffered(Message(client_encryption.export_my_pubkey()))
    # m = s.recv()
    # client_encryption.load_others_pubkey(m.get_plain_msg())

    # # print(f"client pubkey: {hashlib.sha256(client_encryption.export_my_pubkey()).hexdigest()}", type(client_encryption.export_my_pubkey()))
    # # print(f"server pubkey: {hashlib.sha256(client_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(client_encryption.other_pubkey.save_pkcs1()))
    # #############################

    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img30.jpg", "rb") as f:
    #     # m = Message(base64.b64decode(f.read()))
    #     m = Message(f.read())
    # print(m.message)
    # # m = Message("hello server".encode())
    # s.send_buffered(m, e=client_encryption)
    # # s.send_buffered(Message(client_encryption.generate_signature(m.message)), e=client_encryption)
    # m = s.recv(e=client_encryption)
    # print(m)

    #############################TCP2##############################
    # client_socket = ClientSocket("TCP")
    # client_socket.connect(SERVER_ADDRESS)
    # print("connected to server")

    # client_encryption = RSAEncyption()
    # client_encryption.generate_keys()

    # client_socket.send_buffered(Message(client_encryption.export_my_pubkey()))
    # m = client_socket.recv()
    # client_encryption.load_others_pubkey(m.get_plain_msg())

    # print(f"client pubkey: {hashlib.sha256(client_encryption.export_my_pubkey()).hexdigest()}", type(client_encryption.export_my_pubkey()))
    # print(f"server pubkey: {hashlib.sha256(client_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(client_encryption.other_pubkey.save_pkcs1()))
    # ##############################

    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg", "rb") as f:
    #     m = Message(f.read())
    # print("sending image")
    # client_socket.send_buffered(m, e=client_encryption)
    # print("sending signature")
    # sig = Message(client_encryption.generate_signature(m.message))
    # client_socket.send_buffered(sig, e=client_encryption)

    #################TCP AES#######################
    client_socket = ClientSocket("TCP")
    client_socket.connect(SERVER_ADDRESS)
    print("connected to server")

    client_rsa = RSAEncyption()
    client_rsa.generate_keys()

    client_socket.send_buffered(Message(client_rsa.export_my_pubkey()))
    m = client_socket.recv()
    client_rsa.load_others_pubkey(m.get_plain_msg())

    print(f"client pubkey RSA: {hashlib.sha256(client_rsa.export_my_pubkey()).hexdigest()}", type(client_rsa.export_my_pubkey()))
    print(f"server pubkey RSA: {hashlib.sha256(client_rsa.other_pubkey.save_pkcs1()).hexdigest()}", type(client_rsa.other_pubkey.save_pkcs1()))

    client_aes = AESEncryption()
    client_socket.send_buffered(Message(client_aes.key), e=client_rsa)
    print(f"AES key: {hashlib.sha256(client_aes.key).hexdigest()}")

    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\publications_2017_nohagim_aheret_nohagim_nachon.pdf", "rb") as f:
    #     m = Message(f.read())
    m = Message(b"hello!"*100000)
    client_socket.send_buffered(m, e=client_aes)
    # client_socket.send_buffered(m)
    print(hashlib.sha256(m.get_plain_msg()).hexdigest())
    

    ############UDP AES#############################
    # s = ClientSocket()
    # client_rsa = RSAEncyption()
    # client_rsa.generate_keys()

    # ##########key exchange#############
    # s.send_buffered(Message(client_rsa.export_my_pubkey()), SERVER_ADDRESS)
    # m, _ = s.recv()
    # client_rsa.load_others_pubkey(m.get_plain_msg())
    # print(f"client pukey: {hashlib.sha256(client_rsa.export_my_pubkey()).hexdigest()}")
    # print(f"server pukey: {hashlib.sha256(client_rsa.other_pubkey.save_pkcs1()).hexdigest()}")

    # client_aes = AESEncryption()
    # s.send_buffered(Message(client_aes.key), SERVER_ADDRESS, e=client_rsa)
    # print(f"AES key: {hashlib.sha256(client_aes.key).hexdigest()}")

    # with open(r"C:\Users\USER\Desktop\Cyber\PRJ\publications_2017_nohagim_aheret_nohagim_nachon.pdf", "rb") as f:
    #     m = Message(f.read())
    # s.send_buffered(m, SERVER_ADDRESS, e=client_aes)
    # print(hashlib.sha256(m.get_plain_msg()).hexdigest())


if __name__ == "__main__":
    main()
