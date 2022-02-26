from CustomSocket import *
import hashlib
from time import sleep
from select import select
from RSAEncryption import RSAEncyption
from AESEncryption import AESEncryption


class ClientProperties:
    plainsocket = "plainsocket"
    clientsocket = "clientsocket"
    clientname = "clientname"
    client_rsa: "client_rsa"
    rsa = "rsa"
    aes = "aes"


class MultiplexedServer:
    def __init__(self):
        self.server_socket = ServerSocket("TCP")
        self.client_sockets = {}  # {addr: s}
        # self.client_names = {}# {addr, name}
        self.clients = {}  # {addr: {'plainsocket':ps, 'clientsocket': cs, 'clientname':n}}
        self.server_socket.bind_and_listen(("0.0.0.0", 14_000))

    def _select(self):
        client_sockets = list(self.client_sockets.values())
        rlist, wlist, _ = select(
            [self.server_socket.socket] + client_sockets, client_sockets, [], 1)
        print(len(rlist))
        return rlist, wlist

    def read(self):
        print("selecting")
        rlist, wlist = self._select()
        for s in rlist:
            if s is self.server_socket.socket:
                new_client_socket, new_client_addr = self.server_socket.accept()
                new_client_clientsocket_object = ClientSocket.create_client_socket(
                    new_client_socket)
                self.clients[new_client_addr] = {
                    ClientProperties.plainsocket: new_client_socket,
                    ClientProperties.clientsocket: new_client_clientsocket_object,
                    ClientProperties.clientname: None,
                    ClientProperties.rsa: RSAEncyption(),
                    ClientProperties.aes: None
                }
                self.clients[new_client_addr][ClientProperties.rsa].generate_keys()

                self.clients[new_client_addr][ClientProperties.rsa].load_others_pubkey(
                    self.clients[new_client_addr][ClientProperties.clientsocket].recv().get_plain_msg())

                self.clients[new_client_addr][ClientProperties.clientsocket].send(
                    Message(
                        self.clients[new_client_addr][ClientProperties.rsa].export_my_pubkey(
                        )
                    ))

                aes_key = self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.rsa])

                self.clients[new_client_addr][ClientProperties.aes] = AESEncryption(
                    aes_key.get_plain_msg()
                )
                print("===================================================")
                print("New client connected: ", new_client_addr)
                print(
                    f"client pubkey: {hashlib.sha256(self.clients[new_client_addr][ClientProperties.rsa].other_pubkey.save_pkcs1()).hexdigest()}")
                print(
                    f"server pubkey: {hashlib.sha256(self.clients[new_client_addr][ClientProperties.rsa].export_my_pubkey()).hexdigest()}")
                print(
                    f"AES key: {hashlib.sha256(self.clients[new_client_addr][ClientProperties.aes].key).hexdigest()}")
                print("===================================================")


def main():
    m = MultiplexedServer()
    while True:
        m.read()
        sleep(0.07)


if __name__ == "__main__":
    main()
