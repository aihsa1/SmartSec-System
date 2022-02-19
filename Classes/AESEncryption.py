from Crypto.Cipher import AES
import os
from Message import Message


class AESEncryption:
    KEY_SIZE = 16

    def __init__(self, key=None) -> None:
        """
        
        """
        if key is None:
            # encrpyiton mode
            self.key = os.urandom(AESEncryption.KEY_SIZE)
            self.aes = AES.new(self.key, AES.MODE_GCM)
        else:
            # decryption mode
            self.key = key
            self.aes = AES.new(key, AES.MODE_GCM)

    def _new_nonce(self, nonce=None):
        self.aes = AES.new(self.key, AES.MODE_GCM, nonce=nonce)

    def _extract_nonce(self, ciphertext):
        return ciphertext[:AESEncryption.KEY_SIZE]

    def _extract_encrypted_messege(self, ciphertext):
        return ciphertext[AESEncryption.KEY_SIZE:]

    def encrypt(self, plaintext, merged=True):
        self._new_nonce()
        ret = self.aes.nonce, self.aes.encrypt(plaintext)
        if merged:
            return (ret[0] + ret[1])
        return ret

    def decrypt(self, text):
        nonce, ciphertext = self._extract_nonce(
            text), self._extract_encrypted_messege(text)
        self._new_nonce(nonce)
        return self.aes.decrypt(ciphertext)

    def generate_tag(self):
        return self.aes.digest()

    def verify_tag(self, tag):
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
            new_msg = Message.create_message_from_plain_data(cipher2.decrypt(ciphertexts[i]))
        else:
            new_msg += cipher2.decrypt(ciphertexts[i])
        i += 1
        if new_msg.is_complete:
            break
    print(new_msg.message == m.message)



if __name__ == "__main__":
    main()
