from CustomSocket import *
import threading
import hashlib
import cv2
import pickle
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
        self.client_threads = {}
        self.server_socket.bind_and_listen(("0.0.0.0", 14_000))

    def _select(self):
        """
        This method is used to select the sockets that are ready to be read and written to. DO NOT USE THIS METHOD BY ITSELF.
        :return: a list of sockets that are ready to be read and a list of sockets that are ready to be written.
        :rtype: tuple(rlist, wlist)
        """
        client_sockets = list(self.client_sockets.values())
        rlist, wlist, _ = select(
            [self.server_socket.socket] + client_sockets, client_sockets, [], 1)
        return rlist, wlist
    
    def _recv_video(self, addr):
        client = self.clients[addr][ClientProperties.clientsocket]
        client_aes = self.clients[addr][ClientProperties.aes]
        while True:
            try:
                m = client.recv(e=client_aes)
            except ValueError:
                print("client is closed.")
                break
            print("recieved image")

            if cv2.waitKey(10) & 0xFF == ord('q') or len(m.get_plain_msg()) == 0:
                cv2.destroyAllWindows()
                break
            cv2.imshow("image", pickle.loads(m.get_plain_msg()))
        del self.client_threads[addr]

    def read(self):
        """
        This method is responsible of dealing with the sockets that are ready to be read from - reading from the multiplexed server socket.
        """
        rlist, wlist = self._select()
        for s in rlist:
            if s is self.server_socket.socket:
                # adding a new client
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
                self.client_sockets[new_client_addr] = new_client_socket
                # encryption keys preperation
                self.clients[new_client_addr][ClientProperties.rsa].generate_keys()
                self.clients[new_client_addr][ClientProperties.rsa].load_others_pubkey(
                    self.clients[new_client_addr][ClientProperties.clientsocket].recv().get_plain_msg())  # get the public RSA-key of the client
                self.clients[new_client_addr][ClientProperties.clientsocket].send(
                    Message(
                        self.clients[new_client_addr][ClientProperties.rsa].export_my_pubkey(
                        )  # send the public RSA-key of the server
                    ))
                aes_key = self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.rsa])  # get the AES-key of the client
                self.clients[new_client_addr][ClientProperties.aes] = AESEncryption(
                    aes_key.get_plain_msg()
                )  # construct the AESEncryption object
                print("===================================================")
                print("New client connected: ", new_client_addr)
                print(
                    f"client pubkey: {hashlib.sha256(self.clients[new_client_addr][ClientProperties.rsa].other_pubkey.save_pkcs1()).hexdigest()}")
                print(
                    f"server pubkey: {hashlib.sha256(self.clients[new_client_addr][ClientProperties.rsa].export_my_pubkey()).hexdigest()}")
                print(
                    f"AES key: {hashlib.sha256(self.clients[new_client_addr][ClientProperties.aes].key).hexdigest()}")
                print("===================================================")
            else:
                addr = s.getpeername()
                if addr not in self.client_threads.keys():
                    self.client_threads[addr] = threading.Thread(target=self._recv_video, args=(addr,), daemon=True)
                    self.client_threads[addr].start()
                # try:
                #     m = client_socket.recv(e=client_aes)
                #     print("recieved msg")
                #     cv2.imshow(addr.__str__(), pickle.loads(m.get_plain_msg()))
                # except ValueError:
                #     pass


def main():
    pass


if __name__ == "__main__":
    main()
