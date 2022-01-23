import rsa

class RSAEncyption:
    HASH_METHOD = "SHA-256"
    def __init__(self) -> None:
        self.my_keys = None
        self.other_privkey = None
    
    def generate_keys(self):
        self.my_keys = rsa.newkeys(1024)
    
    def encrypt(self, msg):
        return rsa.encrypt(msg.encode(), self.my_keys[0])
    
    def decrypt(self,ciphertext):
        try:
            return rsa.decrypt(ciphertext, self.other_privkey).decode()
        except:
            return False
    
    def generate_signature(self, msg):
        return rsa.sign(msg.encode(), self.my_keys[1], RSAEncyption.HASH_METHOD)
    
    def verify_signature(self, msg, signature):
        try:
            return rsa.verify(msg.encode(), signature, self.other_privkey) == RSAEncyption.HASH_METHOD
        except Exception as e:
            print(e)
            return False

def main():
    client, server = RSAEncyption(), RSAEncyption()
    client.generate_keys(); server.generate_keys()
    ##########start private key key exchange############
    client.other_privkey = server.my_keys[1]; server.other_privkey = client.my_keys[1]
    ##############start key exchange############
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