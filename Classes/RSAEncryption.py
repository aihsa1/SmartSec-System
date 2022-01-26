import hashlib
import rsa


class RSAEncyption:
    HASH_METHOD = "SHA-256"
    KEY_SIZE = 1024
    RECV_BUFFER_SIZE = rsa.common.byte_size(KEY_SIZE)

    def __init__(self) -> None:
        """
        The constructor for the RSAEncyption class. Every instance of this class is used as an interface to the RSA algorithm.
        """
        self.my_pubkey = None
        self.my_privkey = None
        self.other_pubkey = None

    def generate_keys(self):
        """
        This method generates a public and private key pair.
        """
        self.my_pubkey, self.my_privkey = rsa.newkeys(RSAEncyption.KEY_SIZE)

    def export_my_pubkey(self):
        return self.my_pubkey.save_pkcs1()

    def load_others_pubkey(self, pubkey_pkcs1):
        self.other_pubkey = rsa.PublicKey.load_pkcs1(pubkey_pkcs1)

    def encrypt(self, msg):
        """
        Encrypts a message using the senders public key
        :param msg: The message to decrypt
        :type msg: str
        :return: The decrypted message
        :rtype: bytes
        """
        if isinstance(msg, str):
            return rsa.encrypt(msg, self.other_pubkey)
        return rsa.encrypt(msg, self.other_pubkey)

    def decrypt(self, ciphertext):
        """
        Decrypt the incoming ciphertext using our private key. This ciphertext is encrypted by the sender using our public key.
        :param ciphertext: The encrypted message
        :type ciphertext: bytes
        :return: The decrypted message. If something went wrong, False is returned
        """
        # try:
        return rsa.decrypt(ciphertext, self.my_privkey)
        # except Exception as e:
        #     print(e)
        #     return False

    def generate_signature(self, msg):
        """
        This method generates a signature for the given message. The signature is generated using our private key, so the receiver will be able to authenticate the  received message.
        :param msg: The message to sign
        :type msg: str
        """
        if isinstance(msg, str):
            return rsa.sign(msg.encode(), self.my_privkey, RSAEncyption.HASH_METHOD)
        return rsa.sign(msg, self.my_privkey, RSAEncyption.HASH_METHOD)

    def verify_signature(self, msg, signature):
        """
        This method verifies the signature of the given message. The signature is generated using the sender's public key, so we will be able to authenticate the incoming message.
        """
        try:
            return rsa.verify(msg.encode() if isinstance(msg, str) else msg, signature, self.other_pubkey) == RSAEncyption.HASH_METHOD
        except Exception as e:
            print(e)
            return False


def main():
    client, server = RSAEncyption(), RSAEncyption()
    client.generate_keys()
    server.generate_keys()
    ##########start private key key exchange in the public domain############
    # every side gets the other side's public key so he can encrypt
    client.other_pubkey = server.my_pubkey
    server.other_pubkey = client.my_pubkey
    ##############end key exchange############
    msg = input("=> ")
    ciphertext = client.encrypt(msg)
    signature = client.generate_signature(msg)
    ########send message and signature to server#######
    plaintext = server.decrypt(ciphertext)
    if plaintext:
        print(f"plaintext {plaintext}")
    else:
        print("could not decrypt")

    if server.verify_signature(plaintext, signature):
        print("signature verified")
    else:
        print("signature verification failed")


if __name__ == "__main__":
    main()
