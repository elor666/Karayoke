import base64
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import hashlib

BS = 16
def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
def unpad(s): return s[:-ord(s[len(s)-1:])]

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


def generate_AESk_fpub(pub_key):
    """Gets RSA Public key object. Return AES generated encryptor object, RSA Public encrypted number(To create AES key from) in bytes."""
    #pub_key = pickle.loads(recive_until(cli_sock))
    num = random.randint(10,10000)
    encryptorRsa = PKCS1_OAEP.new(RSA.import_key(pub_key))
    #cli_sock.send(encryptorRsa.encrypt(str(num).encode())+b'###')

    #key =hashlib.sha256(str(num).encode("utf-8")).digest()
    encryptor = AESCipher(num)

    return encryptor,encryptorRsa.encrypt(str(num).encode())

def generate_AESk_fpriv(priv_key,encrypted_num): 
    """Gets RSA Private key object, RSA public encrypted number. Returns AES generated encryptor object"""
    decryptor = PKCS1_OAEP.new(RSA.import_key(priv_key))
    decrypted_num = decryptor.decrypt(encrypted_num).decode()

    return AESCipher(decrypted_num)


def generate_RSA_keys():
    """Returns RSA public key, RSA private key of the public key."""
    keyPair = RSA.generate(3072)
    pub_key = keyPair.public_key().export_key('PEM')
    priv_key = keyPair.export_key('PEM')

    return pub_key,priv_key