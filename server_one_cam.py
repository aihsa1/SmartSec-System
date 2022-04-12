import gzip
import hashlib
import cv2
import pickle
import threading
import PySimpleGUI as sg
from Scripts import add_folders_to_path
from Classes.CommunicationCode import CommunicationCode
from Classes.Message import Message
from Screens.detection_gui import generate_detection_gui_server
from Classes.RSAEncryption import RSAEncyption
from Classes.AESEncryption import AESEncryption
from Classes.CustomSocket import ClientSocket, ServerSocket
import numpy as np

frame = None


def comm():
    global frame

    # s = ServerSocket()
    # s.bind_and_listen(("0.0.0.0", 14_000))
    # server_encryption = RSAEncyption()
    # server_encryption.generate_keys()

    # ########key exchange#########
    # m, addr = s.recv()
    # server_encryption.load_others_pubkey(m.get_plain_msg())
    # s.send_buffered(Message(server_encryption.export_my_pubkey()), addr)

    # print(f"client pubkey: {hashlib.sha256(server_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(
    #     server_encryption.other_pubkey.save_pkcs1()))
    # print(f"server pubkey: {hashlib.sha256(server_encryption.export_my_pubkey()).hexdigest()}", type(
    #     server_encryption.export_my_pubkey()))
    # ##########################

    # m, _ = s.recv()
    # print("recieved image")
    # with open("tmp.png", "wb") as f:
    #     f.write(m.get_plain_msg())

    # sig, _ = s.recv(e=server_encryption)
    # print(server_encryption.verify_signature(m.message, sig.get_plain_msg()))

    s = ServerSocket("TCP")
    s.bind_and_listen(("0.0.0.0", 14_000))
    client, addr = s.accept()
    client = ClientSocket.create_client_socket(client)
    server_rsa = RSAEncyption()
    server_rsa.generate_keys()

    ########key exchange#########
    m = client.recv()
    server_rsa.load_others_pubkey(m.get_plain_msg())
    client.send_buffered(
        Message(server_rsa.export_my_pubkey(), code=CommunicationCode.KEY))

    print(f"client pubkey: {hashlib.sha256(server_rsa.other_pubkey.save_pkcs1()).hexdigest()}", type(
        server_rsa.other_pubkey.save_pkcs1()))
    print(f"server pubkey: {hashlib.sha256(server_rsa.export_my_pubkey()).hexdigest()}", type(
        server_rsa.export_my_pubkey()))

    key_message = client.recv(e=server_rsa)
    server_aes = AESEncryption(key=key_message.get_plain_msg())
    print(f"AES key: {hashlib.sha256(server_aes.key).hexdigest()}")

    uname = client.recv(e=server_aes).get_plain_msg()
    passwd = client.recv(e=server_aes).get_plain_msg()
    print(uname, passwd)

    m = client.recv(e=server_aes)
    h, w = pickle.loads(m.get_plain_msg())

    ##########################

    while True:
        try:
            m = client.recv(e=server_aes)
            # m = client.recv()
        except ValueError as e:
            print(e)
            print("client is closed.")
            break
        # print("recieved image")

        if cv2.waitKey(10) & 0xFF == ord('q') or len(m.get_plain_msg()) == 0:
            cv2.destroyAllWindows()
            break
        if m.code.decode() == CommunicationCode.INFO:
            print(m.get_plain_msg())
        else:
            # cv2.imshow("image", pickle.loads(m.get_plain_msg()))
            frame = np.frombuffer(m.get_plain_msg(), dtype=np.uint8)
            frame = np.reshape(frame, (w, h, -1))
            cv2.imshow("image", frame)
            # frame = pickle.loads(m.get_plain_msg())
    client.close()
    s.close()


def gui():
    global frame

    layout, w, h = generate_detection_gui_server()
    window = sg.Window('SmartSec Server', layout, size=(w, h))
    while True:
        event, value = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break
        mutex = threading.Lock()
        mutex.acquire()
        if frame is not None:
            frame_bytes = cv2.imencode(".png", frame)[1].tobytes()
            window["-VIDEO-"].update(data=frame_bytes)
        mutex.release()


def main():
    comm_thread = threading.Thread(target=comm, daemon=True)
    comm_thread.start()
    # gui()
    comm_thread.join()


if __name__ == "__main__":
    main()
