from CustomSocket import *
import threading
import hashlib
import cv2
import pickle
import socket
import numpy as np
from select import select
import PySimpleGUI as sg
from RSAEncryption import RSAEncyption
from AESEncryption import AESEncryption
from ClientProperties import ClientProperties
from CommunicationCode import CommunicationCode
from typing import List, Tuple


class MultiplexedServer:
    cap = cv2.VideoCapture(0)
    WIDTH_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT_WEBCAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    BLACK_SCREEN = cv2.imencode(".png", np.zeros(
        (HEIGHT_WEBCAM // 2, WIDTH_WEBCAM // 2), dtype=np.uint8))[1].tobytes()
    FRAME_PRECENT = 2
    GREEN = (0, 255, 0)# green in BGR format (4 CV2)
    RED = (0, 0, 255)# green in BGR format (4 CV2)
    del cap

    def __init__(self, window) -> None:
        """
        This is the constructor of the class. This function is responsible for initializing the server.
        :param window: the window to display on
        :type window: sg.Window
        """
        self.server_socket = ServerSocket("TCP")
        self.client_sockets = {}  # {addr: s}
        # self.client_names = {}# {addr, name}
        self.clients = {}  # {addr: {'plainsocket':ps, 'clientsocket': cs, 'clientname':n}}
        self.client_threads = {}
        self.server_socket.bind_and_listen(("0.0.0.0", 14_000))
        self.window = window

    def _remove_user_from_lists(self, addr: Tuple[str, int]) -> None:
        """
        This method is used to remove a user from the lists and it is called when a user disconnects. DO NOT USE THIS METHOD BY ITSELF.
        :param addr: the addr of the client - Tuple[ip, port]
        :type addr: Tuple[str, int]
        """
        self.window[f"-VIDEO{tuple(self.client_sockets.keys()).index(addr)}-"].update(
            data=MultiplexedServer.BLACK_SCREEN)
        del self.client_threads[addr]
        del self.client_sockets[addr]
        del self.clients[addr]

    def _select(self) -> Tuple[List[socket.socket], List[socket.socket]]:
        """
        This method is used to select the sockets that are ready to be read and written to. DO NOT USE THIS METHOD BY ITSELF.
        :return: a list of sockets that are ready to be read and a list of sockets that are ready to be written - Tuple[rlist, wlist]
        :rtype: Tuple[List[socket.socket], List[socket.socket]]
        """
        client_sockets = list(self.client_sockets.values())
        rlist, wlist, _ = select(
            [self.server_socket.socket] + client_sockets, client_sockets, [], 1)
        return rlist, wlist
    
    def _draw_incicator_frame(self, img: np.ndarray, found: bool) -> None:
        w, h = img.shape[1], img.shape[0]
        frame_color = MultiplexedServer.GREEN if found else MultiplexedServer.RED
        top_bottom_frame_width = int(w * MultiplexedServer.FRAME_PRECENT / 100)
        left_right_frame_width = int(h * MultiplexedServer.FRAME_PRECENT / 100)

        img[0: top_bottom_frame_width, :, :] = frame_color
        img[top_bottom_frame_width * (-1):, :, :] = frame_color
        img[:, 0: left_right_frame_width, :] = frame_color
        img[:, left_right_frame_width * (-1):, :] = frame_color
        print("drawn")



    def _recv_video(self, addr: Tuple[str, int], window: sg.Window) -> None:
        """

        This auxilary method is used to receive video and to display it.
        :param addr: the addr of the client
        :type addr: Tuple[str, int]
        :param window: the window to display on
        :type window: sg.Window
        """
        client = self.clients[addr][ClientProperties.clientsocket]
        client_aes = self.clients[addr][ClientProperties.aes]
        w, h = self.clients[addr][ClientProperties.webcam_width], self.clients[addr][ClientProperties.webcam_height]
        found_indicator = False
        while True:
            try:
                m = client.recv(e=client_aes)
                # m = client.recv()
            except (ValueError, ConnectionResetError, ConnectionAbortedError) as e:
                print(e)
                print(f"{addr} has disconnected")
                self._remove_user_from_lists(addr)
                break
            # print("recieved image")

            # if cv2.waitKey(10) & 0xFF == ord('q') or len(m.get_plain_msg()) == 0:
            #     cv2.destroyAllWindows()
            #     break
            if len(m.get_plain_msg()) == 0:
                break
            
            mutex = threading.Lock()
            mutex.acquire()
            if m.code.decode() == CommunicationCode.INFO:
                found_indicator = m.get_plain_msg().decode() == "FOUND"
                print(m.get_plain_msg())
            else:
                # cv2.imshow("image", pickle.loads(m.get_plain_msg()))
                # frame = pickle.loads(m.get_plain_msg())
                frame = np.frombuffer(m.get_plain_msg(), dtype=np.uint8)
                frame = np.reshape(frame, (w, h, -1))
                frame = cv2.resize(frame, dsize=(
                    MultiplexedServer.WIDTH_WEBCAM // 2, MultiplexedServer.HEIGHT_WEBCAM // 2))
                self._draw_incicator_frame(frame, found_indicator)
                frame_bytes = cv2.imencode(".png", frame)[1].tobytes()
                try:
                    window[f"-VIDEO{tuple(self.client_sockets.keys()).index(addr)}-"].update(
                        data=frame_bytes)
                except Exception as e:
                    mutex.release()
                    print(e)
                    return
            mutex.release()

    def read(self) -> None:
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
                        # send the public RSA-key of the server
                        self.clients[new_client_addr][ClientProperties.rsa].export_my_pubkey(), code=CommunicationCode.KEY
                    ))
                aes_key = self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.rsa])  # get the AES-key of the client
                self.clients[new_client_addr][ClientProperties.aes] = AESEncryption(
                    aes_key.get_plain_msg()
                )  # construct the AESEncryption object
                # get the dimensions of the webcam of the new client
                h, w = pickle.loads(self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.aes]
                ).get_plain_msg())
                self.clients[new_client_addr][ClientProperties.webcam_width] = w
                self.clients[new_client_addr][ClientProperties.webcam_height] = h
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
                    self.client_threads[addr] = threading.Thread(
                        target=self._recv_video, args=(addr, self.window), daemon=True)
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
