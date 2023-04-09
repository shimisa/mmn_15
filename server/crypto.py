import os
import rsa

key = os.urandom(256 // 8)


def generate_keys():
    (publicKey, privateKey) = rsa.newkeys(1024)

    with open('keys/publicKey.pem', 'wb') as p:
        p.write(publicKey.save_pkcs1('PEM'))
    with open('keys/privateKey.pem', 'wb') as p:
        p.write(privateKey.save_pkcs1('PEM'))


def load_keys():
    with open('keys/publicKey.pem', 'rb') as p:
        public_key = rsa.PublicKey.load_pkcs1(p.read())
    with open('keys/privateKey.pem', 'rb') as p:
        private_key = rsa.PrivateKey.load_pkcs1(p.read())
    return private_key, public_key


def encrypt(message, key):
    return rsa.encrypt(message.encode('ascii'), key)


def decrypt(ciphertext, key):
    # try:
    return rsa.decrypt(ciphertext, key).decode('ascii')
    # except:
    #     return False


def sign(message, key):
    return rsa.sign(message.encode('ascii'), key, 'SHA-1')


def verify(message, signature, key):
    try:
        return rsa.verify(message.encode('ascii'), signature, key, ) == 'SHA-1'
    except:
        return False

