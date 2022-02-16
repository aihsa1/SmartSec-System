from Crypto.Cipher import AES
import os


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

    # def _increment_nonce(self):
    #     new_nonce_int = int.from_bytes(self.aes.nonce, "big") + 1
    #     byte_size = len(self.aes.nonce)
    #     try:
    #         self.aes.nonce = int.to_bytes(new_nonce_int, byte_size, "big")
    #     except OverflowError:
    #         self.aes.nonce = int.to_bytes(new_nonce_int, byte_size + 1, "big")

    # def _decrement_nonce(self):
    #     new_nonce_int = int.from_bytes(self.aes.nonce, "big") - 1
    #     byte_size = len(self.aes.nonce)
    #     try:
    #         self.aes.nonce = int.to_bytes(
    #             new_nonce_int, byte_size, "big").replace(b'\x00', b"", 1)
    #     except OverflowError:
    #         self.aes.nonce = int.to_bytes(
    #             new_nonce_int, byte_size + 1, "big").replace(b'\x00', b"", 1)
    #     print(f"nonce: {self.aes.nonce}")

    def _new_nonce(self, nonce=None):
        self.aes = AES.new(self.key, AES.MODE_GCM, nonce=nonce)

    def _extract_nonce(self, ciphertext):
        return ciphertext[:AESEncryption.KEY_SIZE]

    def _extract_encrypted_messege(self, ciphertext):
        return ciphertext[AESEncryption.KEY_SIZE:]

    def encrypt(self, plaintext):
        self._new_nonce()
        ret = self.aes.nonce, self.aes.encrypt(plaintext)
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
    
    cipher = AESEncryption()
    plaintext = b"Hello World"
    cipher2 = AESEncryption(cipher.key)
    for _ in range(20):
        nonce, ciphertext = cipher.encrypt(plaintext)
        tag = cipher.generate_tag()
        plaintext2 = cipher2.decrypt(nonce + ciphertext)
        print(cipher2.verify_tag(tag))
        print(nonce)

        print(plaintext2)
        nonce, ciphertext = cipher2.encrypt(plaintext)
        tag = cipher2.generate_tag()        
        plaintext2 = cipher.decrypt(nonce + ciphertext)
        print(cipher.verify_tag(tag))
        print(nonce)
        print(plaintext2)



if __name__ == "__main__":
    main()
