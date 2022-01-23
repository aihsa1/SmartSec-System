import rsa

class RSAEncyption:
    HASH_METHOD = "SHA-256"
    def __init__(self) -> None:
        self.my_pubkey = None
        self.my_privkey = None
        self.other_pubkey = None
    
    def generate_keys(self):
        self.my_pubkey, self.my_privkey = rsa.newkeys(1024)
    
    def encrypt(self, msg):
        """
        Encrypt a message using the senders public key
        :param msg: The message to decrypt
        :type msg: str
        :return: The decrypted message
        :rtype: bytes
        """
        return rsa.encrypt(msg.encode(), self.other_pubkey)
    
    def decrypt(self, ciphertext):
        """
        Decrypt the incoming message using our private key
        :param ciphertext: The encrypted message
        :type ciphertext: bytes
        :return: The decrypted message
        """
        try:
            return rsa.decrypt(ciphertext, self.my_privkey).decode()
        except:
            return False
    
    def generate_signature(self, msg):
        return rsa.sign(msg.encode(), self.my_privkey, RSAEncyption.HASH_METHOD)
    
    def verify_signature(self, msg, signature):
        try:
            return rsa.verify(msg.encode(), signature, self.other_pubkey) == RSAEncyption.HASH_METHOD
        except Exception as e:
            print(e)
            return False

def main():
    client, server = RSAEncyption(), RSAEncyption()
    client.generate_keys(); server.generate_keys()
    ##########start private key key exchange############
    # every side gets the other side's public key so he can encrypt
    client.other_pubkey = server.my_pubkey; server.other_pubkey = client.my_pubkey
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