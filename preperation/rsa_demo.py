import rsa

HASH_METHOD = "SHA-256"


def generate_keys():
    pubkey, privkey = rsa.newkeys(1024)
    with open("public.pem", "wb") as f:
        f.write(pubkey.save_pkcs1())
    with open("private.pem", "wb") as f:
        f.write(privkey.save_pkcs1())


def load_keys():
    with open("public.pem", "rb") as f:
        pubkey = rsa.PublicKey.load_pkcs1(f.read())
    with open("private.pem", "rb") as f:
        privkey = rsa.PrivateKey.load_pkcs1(f.read())
    return pubkey, privkey


def encrypt(msg, pubkey):
    return rsa.encrypt(msg.encode(), pubkey)


def decrypt(ciphertext, privkey):
    try:
        return rsa.decrypt(ciphertext, privkey).decode()
    except:
        return False


def generate_signature(msg, privkey):
    return rsa.sign(msg.encode(), privkey, HASH_METHOD)


def verify_signature(msg, signature, pubkey):
    try:
        return rsa.verify(msg.encode(), signature, pubkey) == HASH_METHOD
    except Exception as e:
        print(e)
        return False


def main():
    generate_keys()
    pubkey, privkey = load_keys()
    msg = input("=> ")
    ciphertext = encrypt(msg, pubkey)
    signature = generate_signature(msg, privkey)
    print(f"ciphertext {ciphertext}")
    print(f"signature {signature}")
    ###########################
    plaintext = decrypt(ciphertext, privkey)
    if plaintext:
        print(f"plaintext {plaintext}")
    else:
        print("could not decrypt")
    if verify_signature(plaintext, signature, pubkey):
        print("signature verified")
    else:
        print("signature verification failed")


if __name__ == "__main__":
    main()
