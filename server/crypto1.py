from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import zlib

class Crypto:

    def _generate_keys(self):
        # (publicKey, privateKey) = rsa.newkeys(1024)
        key_pair = RSA.generate(1024)
        public_key = key_pair.publickey().exportKey()
        private_key = key_pair.exportKey()

        print(private_key)
        print(public_key)

        with open('keys/publicKey1.pem', 'wb') as p:
            p.write(public_key)
        with open('keys/privateKey1.pem', 'wb') as p:
            p.write(private_key)

    def load_keys(self):
        with open('keys/publicKey1.pem', 'rb') as p:
            public_key = p.read()
        with open('keys/privateKey1.pem', 'rb') as p:
            private_key = p.read()
        return private_key, public_key

    def encrypt(self, text, key):
        public_key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(public_key)
        ciphertext = cipher.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext, key):
        private_key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(private_key)
        decrypted_text = cipher.decrypt(ciphertext)
        return decrypted_text

    def aes_decrypt(self, aes_session_key, data):
        IV = b"                "
        cipher_aes = AES.new(aes_session_key, AES.MODE_CFB, IV)
        return cipher_aes.decrypt(data)

    def generate_aes_key(self):
        session_key = get_random_bytes(16)
        return session_key

    def crc(self, content):
        """
        Calculates the CRC-32 checksum of the given data.
        """
        return zlib.crc32(content) & 0xffffffff


