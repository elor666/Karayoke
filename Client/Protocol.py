from encryption import AESCipher
import socket

def send_msg(sock:socket.socket, encryptor:AESCipher,msg,code : str):

  enc_msg = encryptor.encrypt(msg)

  len_msg = str(len(enc_msg)).zfill(10).encode()

  sock.send(len_msg+code.encode()+enc_msg)


def recieve_msg(sock:socket.socket, encryptor:AESCipher):
  """Return msg code, msg in bytes"""
  len_msg = int(sock.recv(10))

  code = str(sock.recv(3))

  enc_msg = sock.recv(len_msg)

  return code,encryptor.decrypt(enc_msg)