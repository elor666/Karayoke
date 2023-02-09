import socket
import threading
import encryption
from database import DataBase

FINISH = False
DATA_BASE = None

def encrypt_connection(sock:socket.socket):
  pub, priv = encryption.generate_RSA_keys()

  print("RSA keys created!")


  len_msg = str(len(pub)).zfill(10).encode()
  sock.send(len_msg+b'PUB'+pub)

  len_msg = int(sock.recv(10))
  code = (sock.recv(3)).decode()
  if code == "PUB":
    rsa_num = sock.recv(len_msg)
    return encryption.generate_AESk_fpriv(priv,rsa_num)
  else:
    return False


def login_register(sock: socket.socket,encryptor : encryption.AESCipher):
  global DATA_BASE
  finish = False

  while not finish:
    cod,msg = encryptor.recieve_msg(sock)
    if cod == "LOG":
      user,password = msg.decode().split("#")
      res = DATA_BASE.login(user,password)
      print(res)
    elif cod == "REG":
      user,password = msg.decode().split("#")
      res = DATA_BASE.register(user,password)
    else:
      encryptor.send_msg(sock,"","FAL")
    if res:
      print(user,password,res)
      encryptor.send_msg(sock,"","SUC")
      finish = True
    else:
      encryptor.send_msg(sock,"","FAL")
  
  return True

def handle_client(sock:socket.socket):

  print("started to handle client")
  encryptor = encrypt_connection(sock)
  if not encryptor:
    print("faild to encrypt")
  else:
    print("Connected to client with", encryptor)
    print(login_register(sock,encryptor))


def client_disconnect(threads):
  for t,cli in threads:
    pass


def main():
  global FINISH
  global DATA_BASE

  DATA_BASE = DataBase()


  sock = socket.socket()
  port = 12000

  sock.bind(('0.0.0.0',port))
  sock.listen(5)

  threads = []

  print("waiting for clients!")

  while not FINISH:
    cli, addr = sock.accept()
    print(addr,"connected")
    t = threading.Thread(target=handle_client, args=[cli])
    t.start()
    threads.append([t,cli])


if __name__ == '__main__':
  main()