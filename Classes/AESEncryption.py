from Crypto.Cipher import AES
import os
from Message import Message
from typing import Tuple, Union


class AESEncryption:
    """
    This class is an interface to the AES encryption algorithm. It is used to encrypt and decrypt messages easily.
    :var KEY_SIZE: The size of the key used for encryption and decryption.
    :type KEY_SIZE: int
    """
    KEY_SIZE = 16

    def __init__(self, key: bytes = None) -> None:
        """
        This is the constructor for the AESEncryption class. Every object is used as an interface to the AES encryption algorithm.
        :param key: The key used for encryption and decryption. If no key is provided, a random key is generated. Otherwise, the key is used.
        :type key: bytes
        """
        if key is None:
            # encrpyiton mode
            self.key = os.urandom(AESEncryption.KEY_SIZE)
            self.aes = AES.new(self.key, AES.MODE_GCM)
        else:
            # decryption mode
            self.key = key
            self.aes = AES.new(key, AES.MODE_GCM)

    def _new_nonce(self, nonce: bytes = None) -> None:
        """
        This method updates the nonce used for encryption and decryption. if no nonce is provided, it will be used instead of a random one.
        :param nonce: The nonce to use. If no nonce is provided, a random one will be generated.
        :type nonce: bytes
        """
        self.aes = AES.new(self.key, AES.MODE_GCM, nonce=nonce)

    def _extract_nonce(self, ciphertext: bytes) -> bytes:
        """
        This auxiliary method extracts the nonce from the ciphertext.
        :param ciphertext: The ciphertext to extract the nonce from.
        :type ciphertext: bytes
        :return: The nonce
        :rtype: bytes
        """
        return ciphertext[:AESEncryption.KEY_SIZE]

    def _extract_encrypted_messege(self, ciphertext: bytes) -> bytes:
        """
        This auxiliary method extracts the cipher from the data recieved.
        :param ciphertext: The ciphertext to extract the cipher from.
        :type ciphertext: bytes
        :return: The cipher
        :rtype: bytes
        """
        return ciphertext[AESEncryption.KEY_SIZE:]

    def encrypt(self, plaintext, merged: bool = True) -> Union[Tuple, bytes]:
        """
        This method encrypts the given plaintext.
        :param plaintext: The plaintext to encrypt
        :type plaintext: bytes
        :param merged: If True, the nonce and ciphertext are merged into one string of bytes. If False, the nonce and ciphertext are returned separately (as a tuple).
        :type merged: bool
        :return:  (nonce + ciphertext) or (nonce, ciphertext)
        :rtype: Union[Tuple, bytes]
        """
        self._new_nonce()
        ret = self.aes.nonce, self.aes.encrypt(plaintext)
        if merged:
            return (ret[0] + ret[1])
        return ret

    def decrypt(self, text: bytes) -> bytes:
        """
        This method decrypts the given ciphertext. NOTE that the nonce should be in the text and before the ciphertext.
        :param text: A string of bytes containing the nonce and ciphertext. It should be as received from the encrypt() method.
        :type text: bytes
        :return: The plaintext
        :rtype: bytes
        """
        nonce, ciphertext = self._extract_nonce(
            text), self._extract_encrypted_messege(text)
        self._new_nonce(nonce)
        return self.aes.decrypt(ciphertext)

    def generate_tag(self) -> bytes:
        """
        This method generates a tag for the current nonce. The tag is used to verify the integrity and authenticity of the message.
        :return: The tag
        :rtype: bytes
        """
        return self.aes.digest()

    def verify_tag(self, tag: bytes) -> bool:
        """
        This method verifies the integrity and authenticity of the message.
        :param tag: The tag to verify.
        :type tag: bytes
        :return: True if the tag is valid, False otherwise.
        :rtype: bool
        """
        try:
            return self.aes.verify(tag) is None
        except ValueError:
            return False


def main():
    # cipher = AESEncryption()
    # plaintext = b"Hello World"
    # cipher = AESEncryption()
    # cipher2 = AESEncryption(cipher.key)

    # for _ in range(20):
    #     nonce, ciphertext = cipher.encrypt(plaintext)
    #     print(nonce)
    #     tag = cipher.generate_tag()
    #     plaintext2 = cipher2.decrypt(nonce + ciphertext)
    #     print(plaintext2, cipher2.verify_tag(tag[:]))
    # print("------------------------transition------------------")
    # plaintext = b"Hello World"
    # for _ in range(20):
    #     nonce, ciphertext = cipher2.encrypt(plaintext)
    #     print(nonce)
    #     tag = cipher2.generate_tag()
    #     plaintext = cipher.decrypt(nonce + ciphertext)
    #     print(plaintext2, cipher.verify_tag(tag[:]))
    # ----------------------------------------------------------------------------------

    # cipher = AESEncryption()
    # plaintext = b"Hello World"*(10**7)
    # cipher2 = AESEncryption(cipher.key)
    # for _ in range(20):
    #     nonce, ciphertext = cipher.encrypt(plaintext, False)
    #     tag = cipher.generate_tag()
    #     plaintext2 = cipher2.decrypt(nonce + ciphertext)
    #     print(cipher2.verify_tag(tag))
    #     print(nonce)
    #     # print(plaintext2)

    #     nonce, ciphertext = cipher2.encrypt(plaintext, False)
    #     tag = cipher2.generate_tag()
    #     plaintext2 = cipher.decrypt(nonce + ciphertext)
    #     print(cipher.verify_tag(tag))
    #     print(nonce)
    #     # print(plaintext2)

    # m = Message(b"hi"*(10**5))
    # indicies1 = list(m.splitted_data_generator(4096))

    # cipher = AESEncryption()
    # ciphertexts = []
    # for start, end in indicies1:
    #     ciphertexts.append(cipher.encrypt(m.message[start:end]))

    # cipher2 = AESEncryption(cipher.key)
    # plaintexts = []
    # for c in ciphertexts:
    #     plaintexts.append(cipher2.decrypt(c))
    # print(plaintexts == [m.message[start:end] for start, end in indicies1])

    m = Message(b"hi"*(10**4))
    indicies1 = list(m.splitted_data_generator(4096))
    cipher = AESEncryption()
    ciphertexts = []
    for start, end in indicies1:
        ciphertexts.append(cipher.encrypt(m.message[start:end]))

    cipher2 = AESEncryption(cipher.key)
    i = 0
    while True:
        if "new_msg" not in locals():
            new_msg = Message.create_message_from_plain_data(
                cipher2.decrypt(ciphertexts[i]))
        else:
            new_msg += cipher2.decrypt(ciphertexts[i])
        i += 1
        if new_msg.is_complete:
            break
    print(new_msg.message == m.message)


if __name__ == "__main__":
    main()
