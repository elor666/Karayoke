import base64
import hashlib
import random
import socket

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA

DEBUG = True
MAX_LEN_PRINT = 100

BS = 16
def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
def unpad(s): return s[:-ord(s[len(s) - 1:])]


class AESCipher:
    def __init__(self, num):
        self.key = hashlib.sha256(str(num).encode("utf-8")).digest()

    def encrypt(self, raw):
        raw = pad(raw)
        raw = raw.encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))

    def send_msg(self, sock: socket.socket, msg: str, code: str):

        enc_msg = self.encrypt(code + msg)

        len_msg = str(len(enc_msg)).zfill(10).encode()

        sock.send(len_msg + enc_msg)

        if DEBUG:
            print("sent>>", code + "#" + msg[:min(len(msg), MAX_LEN_PRINT)])

    def recieve_msg(self, sock: socket.socket):
        """Return msg code, msg in bytes"""

        len_msg = b''

        while len(len_msg) < 10:
            _s = sock.recv(10 - len(len_msg))
            if _s == b'':
                len_msg = b''
                break
            len_msg += _s

        len_msg = int(len_msg) if len_msg != b'' else b''

        enc_msg = b''
        if len_msg != b'':
            while len(enc_msg) < len_msg:
                _d = sock.recv(len_msg - len(enc_msg))

                if _d == b'':
                    enc_msg = b''
                    break

                enc_msg += _d

        if enc_msg == b'':
            raise Exception("DISCONNECT")

        dec_msg = self.decrypt(enc_msg)
        code, msg = dec_msg[:3], dec_msg[3:]

        if DEBUG:
            print("recived>>", code.decode(),
                  msg[:min(len(msg), MAX_LEN_PRINT)])

        return code.decode(), msg


def generate_AESk_fpub(pub_key):
    """Gets RSA Public key object. Return AES generated encryptor object, RSA Public encrypted number(To create AES key from) in bytes."""
    num = random.randint(10, 10000)
    encryptorRsa = PKCS1_OAEP.new(RSA.import_key(pub_key))
    encryptor = AESCipher(num)

    return encryptor, encryptorRsa.encrypt(str(num).encode())


def generate_AESk_fpriv(priv_key, encrypted_num):
    """Gets RSA Private key object, RSA public encrypted number. Returns AES generated encryptor object"""
    decryptor = PKCS1_OAEP.new(RSA.import_key(priv_key))
    decrypted_num = decryptor.decrypt(encrypted_num).decode()

    return AESCipher(decrypted_num)


def generate_RSA_keys():
    """Returns RSA public key, RSA private key of the public key."""
    keyPair = RSA.generate(3072)
    pub_key = keyPair.public_key().export_key('PEM')
    priv_key = keyPair.export_key('PEM')

    return pub_key, priv_key
