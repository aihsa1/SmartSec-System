import gzip
import hashlib
import cv2
import pickle
from Scripts import add_classes_to_path
from Classes.Message import Message
from Classes.RSAEncryption import RSAEncyption
from Classes.CustomSocket import ClientSocket, ServerSocket

def comm():
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
    server_encryption = RSAEncyption()
    server_encryption.generate_keys()

    ########key exchange#########
    m = client.recv()
    server_encryption.load_others_pubkey(m.get_plain_msg())
    client.send_buffered(Message(server_encryption.export_my_pubkey()))

    print(f"client pubkey: {hashlib.sha256(server_encryption.other_pubkey.save_pkcs1()).hexdigest()}", type(
        server_encryption.other_pubkey.save_pkcs1()))
    print(f"server pubkey: {hashlib.sha256(server_encryption.export_my_pubkey()).hexdigest()}", type(
        server_encryption.export_my_pubkey()))
    ##########################

    # m = client.recv(e=server_encryption)
    m = client.recv()
    print("recieved image")
    # with open("tmp.png", "wb") as f:
    #     f.write(cv2.imencode(".png", pickle.loads(m.get_plain_msg()))[1].tobytes())
    
    # sig = client.recv(e=server_encryption)
    # print(server_encryption.verify_signature(m.message, sig.get_plain_msg()))
    
    while True:
        cv2.imshow("image", pickle.loads(m.get_plain_msg()))
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    client.close()
    s.close


if __name__ == "__main__":
    comm()