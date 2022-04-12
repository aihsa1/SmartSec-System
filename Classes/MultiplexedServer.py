from datetime import datetime
import cv2
import pickle
import socket
import hashlib
import datetime
import threading
import numpy as np
from time import sleep
from Timer import Timer
from queue import Queue
import PySimpleGUI as sg
from select import select
from CustomSocket import *
from typing import List, Tuple
from RSAEncryption import RSAEncyption
from AESEncryption import AESEncryption
from PyMongoInterface import PyMongoInterface
from ClientProperties import ClientProperties
from CommunicationCode import CommunicationCode


class MultiplexedServer:
    DB_INSERT_TIMER_DELAY = 20
    MAX_QUEUED_INCIDENTS = 3

    with open(os.path.join("Configs", "dimensions.json"), "r") as f:
        WIDTH_WEBCAM, HEIGHT_WEBCAM = json.load(f).values()

    BLACK_SCREEN = cv2.imencode(".png", np.zeros(
        (HEIGHT_WEBCAM // 2, WIDTH_WEBCAM // 2), dtype=np.uint8))[1].tobytes()
    FRAME_PRECENT = 2
    GREEN = (0, 255, 0)  # green in BGR format (4 CV2)
    RED = (0, 0, 255)  # green in BGR format (4 CV2)

    SAVED_IMG_SIZE = (250, 200)

    def __init__(self, window) -> None:
        """
        This is the constructor of the class. This function is responsible for initializing the server.
        :param window: the window to display on
        :type window: sg.Window
        """
        self.server_socket = ServerSocket("TCP")
        self.client_sockets = {}  # {addr: s} - a dict contains the plain sockets
        self.clients = {}  # {addr: {'plainsocket':ps, 'clientsocket': cs, 'clientname':n}} - a dict contains the clients and all of their conponents
        self.client_threads = {}  # {addr: t} - a dict contains the threads of the clients
        self.server_socket.bind_and_listen(("0.0.0.0", 14_000))
        self.window = window  # the video GUI of the server
        self.db = PyMongoInterface()  # the database of the server
        # the insert queue to the database
        self.insert_queue = Queue(MultiplexedServer.MAX_QUEUED_INCIDENTS)
        # indicates that the server is shutting down and the insert queue should be dumped to the DB
        self.final_dump_flag = False

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

    def _remove_user_from_lists(self, addr: Tuple[str, int]) -> None:
        """
        This method is used to remove a user from the lists and it is called when a user disconnects. DO NOT USE THIS METHOD BY ITSELF.
        :param addr: the addr of the client - Tuple[ip, port]
        :type addr: Tuple[str, int]
        """
        self.window[f"-VIDEO{tuple(self.client_sockets.keys()).index(addr)}-"].update(
            data=MultiplexedServer.BLACK_SCREEN)
        try:
            del self.client_threads[addr]
        except KeyError:
            pass
        del self.client_sockets[addr]
        del self.clients[addr]

    def _draw_indicator_frame(self, img: np.ndarray, frame_color: tuple) -> None:
        """
        This method is used to draw the indicator frame around the image.
        :param img: the image to draw the indicator frame on (by reference)
        :type img: np.ndarray
        :param frame_color: the color of the indicator frame in BGR
        :type frame_color: tuple
        """
        w, h = img.shape[1], img.shape[0]
        top_bottom_frame_width = int(w * MultiplexedServer.FRAME_PRECENT / 100)
        left_right_frame_width = int(h * MultiplexedServer.FRAME_PRECENT / 100)

        img[0: top_bottom_frame_width, :, :] = frame_color
        img[top_bottom_frame_width * (-1):, :, :] = frame_color
        img[:, 0: left_right_frame_width, :] = frame_color
        img[:, left_right_frame_width * (-1):, :] = frame_color

    def _dump_insert_queue(self):
        """
        This method is used to dump the insert queue to the database intermittently.
        Dumping occurs every 20 seconds. or every time the insert queue is full (3 by default).
        DO NOT USE THIS METHOD BY ITSELF.
        """
        t = Timer()
        while True:
            sleep(0.2)
            mutex = threading.Lock()
            mutex.acquire()
            if self.final_dump_flag:
                break
            if self.insert_queue.full() or (t.elapsed_time() > MultiplexedServer.DB_INSERT_TIMER_DELAY and not self.insert_queue.empty()):
                self.db.insert(*self.insert_queue.queue,
                               db_name="SmartSecDB", col_name="Pistols")
                print("inserted queue to db")
                self.insert_queue = Queue(
                    MultiplexedServer.MAX_QUEUED_INCIDENTS)
                t.update_time()
            mutex.release()

        mutex = threading.Lock()
        mutex.acquire()
        if not self.insert_queue.empty():
            self.db.insert(*self.insert_queue.queue,
                           db_name="SmartSecDB", col_name="Pistols")
            print(
                f"dumped {self.insert_queue.qsize()} items to db. Now shutting down.")
        mutex.release()

    def _report_incident(self, addr: Tuple[str, int], img: np.ndarray) -> None:
        """
        This method is used to report an incident to the database. This is done by adding the incident to the insert queue
        :param addr: the addr of the client - Tuple[ip, port]
        :type addr: Tuple[str, int]
        :param img: the image of the incident
        :type img: np.ndarray
        """
        dtype = np.dtype(img.dtype).__str__()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        date = datetime.datetime.now()
        mutex = threading.Lock()
        mutex.acquire()
        print(self.insert_queue.qsize())
        self.insert_queue.put_nowait({"addr": addr, "img": img_bytes, "dtype": dtype,
                                      "date": date})
        mutex.release()

    def insert_queue_checker(self) -> threading.Thread:
        """
        This method is used to create a thread that checks the insert queue periodically. The thread is started automatically
        :return: a reference to the thread (so it can be join in other places)
        :rtype: threading.Thread
        """
        t = threading.Thread(target=self._dump_insert_queue, daemon=True)
        t.start()
        return t

    def final_insert_queue_dump(self):
        """
        This method is used to indicate to the insert_queue_checker_thread to dump the insert queue to the database.
        """
        self.final_dump_flag = True

    def _check_user(self, uname: bytes, passwd: bytes):
        return len(tuple(self.db.find({"uname": uname.decode(), "passwd": hashlib.sha512(passwd).hexdigest()}, db_name="SmartSecDB", col_name="Users"))) == 1

    def _recv_video(self, addr: Tuple[str, int], window: sg.Window) -> None:
        """

        This auxilary method is used to receive video and to display it. DO NOT USE THIS METHOD BY ITSELF.
        :param addr: the addr of the client
        :type addr: Tuple[str, int]
        :param window: the window to display on
        :type window: sg.Window
        """
        client = self.clients[addr][ClientProperties.clientsocket]
        client_aes = self.clients[addr][ClientProperties.aes]
        w, h = self.clients[addr][ClientProperties.webcam_width], self.clients[addr][ClientProperties.webcam_height]
        found_indicator = False
        reported_indicator = False
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

                if found_indicator:
                    color = MultiplexedServer.GREEN
                    if not reported_indicator:
                        self._report_incident(addr, cv2.resize(
                            frame, dsize=MultiplexedServer.SAVED_IMG_SIZE))
                        reported_indicator = True
                else:
                    color = MultiplexedServer.RED
                    reported_indicator = False
                self._draw_indicator_frame(frame, color)
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

                uname = self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.aes]
                ).get_plain_msg()
                passwd = self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.aes]
                ).get_plain_msg()
                print(uname, passwd)
                
                if self._check_user(uname, passwd):
                    self.clients[new_client_addr][ClientProperties.clientsocket].send(
                    Message(
                        "OK", code=CommunicationCode.INFO
                    ), e=self.clients[new_client_addr][ClientProperties.aes])

                else:
                    self.clients[new_client_addr][ClientProperties.clientsocket].send(
                    Message(
                        "E", code=CommunicationCode.INFO
                    ), e=self.clients[new_client_addr][ClientProperties.aes])
                    self._remove_user_from_lists(new_client_addr)
                    continue

                # get the dimensions of the webcam of the new client
                h, w = pickle.loads(self.clients[new_client_addr][ClientProperties.clientsocket].recv(
                    e=self.clients[new_client_addr][ClientProperties.aes]
                ).get_plain_msg())
                self.clients[new_client_addr][ClientProperties.webcam_width] = w
                self.clients[new_client_addr][ClientProperties.webcam_height] = h

                print("===================================================")
                print("New client connected: ", new_client_addr)
                print(
                    f"client pubkey: {hashlib.sha512(self.clients[new_client_addr][ClientProperties.rsa].other_pubkey.save_pkcs1()).hexdigest()}")
                print(
                    f"server pubkey: {hashlib.sha512(self.clients[new_client_addr][ClientProperties.rsa].export_my_pubkey()).hexdigest()}")
                print(
                    f"AES key: {hashlib.sha512(self.clients[new_client_addr][ClientProperties.aes].key).hexdigest()}")
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
