import base64
import pickle
import socket
import threading
from io import BytesIO
from pathlib import Path

import encryption
from database import DataBase
from lyrics import download_song_lyrics, search_result
from split import separate_song
from sync import auto_sync_lyrics

FINISH = False
DATA_BASE = None
SONG_LOCK = threading.Lock()

PUB_KEY = None
PRIV_KEY = None

def encrypt_connection(sock: socket.socket):
    global PUB_KEY,PRIV_KEY
    pub, priv = PUB_KEY,PRIV_KEY    #encryption.generate_RSA_keys()


    len_msg = str(len(pub)).zfill(10).encode()
    sock.send(len_msg + b'PUB' + pub)

    len_msg = b''

    while len(len_msg) < 10:
        _s = sock.recv(10 - len(len_msg))
        if _s == b'':
            len_msg = b''
            break
        len_msg += _s

    len_msg = int(len_msg) if len_msg != b'' else b''

    code = b''

    while len(code) < 3:
        _s = sock.recv(3 - len(code))
        if _s == b'':
            code = b''
            break
        code += _s

    code = code.decode()

    if code == "PUB":
        rsa_num = b''
        if len_msg != b'':
            while len(rsa_num) < len_msg:
                _d = sock.recv(len_msg - len(rsa_num))

                if _d == b'':
                    rsa_num = b''
                    break

                rsa_num += _d

        return encryption.generate_AESk_fpriv(priv, rsa_num)
    else:
        return False


def login_register_loop(sock: socket.socket, encryptor: encryption.AESCipher):
    global DATA_BASE
    finish = False
    try:
        while not finish:
            cod, msg = encryptor.recieve_msg(sock)
            if cod == "LOG":
                user, password = msg.decode().split("#")
                res = DATA_BASE.login(user, password)
            elif cod == "REG":
                user, password = msg.decode().split("#")
                res = DATA_BASE.register(user, password)
            else:
                encryptor.send_msg(sock, "", "FAL")
            if res:
                encryptor.send_msg(sock, "", "SUC")
                finish = True
            elif cod == "EXT":
                return False
            else:
                encryptor.send_msg(sock, "", "FAL")
    except Exception as err:
        print(err)
        return False

    return True


def get_fileobject(out_file):
    file_object = BytesIO()
    with open(out_file, "rb") as file:
        file_object.write(file.read())

        print("File opened")

        file_object.seek(0)

        pickled_file = base64.b64encode(pickle.dumps(file_object)).decode()

        return pickled_file


def get_times(times_path):
    with open(times_path, "r") as f:
        time_list = f.readlines()
        time_list = [float(time[:-1]) if time[-1] ==
                     '\n' else float(time) for time in time_list]
    return base64.b64encode(pickle.dumps(time_list)).decode()


def get_lyr(path):
    with open(path, "r") as f:
        lyrics = f.readlines()
    lyrics = [line[:-1] if line[-1] ==
              '\n' else line for line in lyrics if line != "\n"]
    return base64.b64encode(pickle.dumps(lyrics)).decode()


def song_search_loop(sock: socket.socket, encryptor: encryption.AESCipher):
    artist = ""
    song = ""
    MY_SONG = False  # if the song is in server folder
    while True:
        code, msg = encryptor.recieve_msg(sock)

        if code == "SCH":
            msg = msg.decode()
            artist, song = msg.split("#")
            result = search_result(artist, song)
            if f"{artist} {song}" in result:
                MY_SONG = True
            else:
                MY_SONG = False
            encryptor.send_msg(
                sock, base64.b64encode(
                    pickle.dumps(result)).decode(), "SCH")

        elif code == "RES" or code == "REV":
            choice, auto_sync = int(
                msg.split(b"#")[0]), int(
                msg.split(b"#")[1])
            if not MY_SONG:
                SONG_LOCK.acquire()
                out_file = download_song_lyrics(artist, song, choice)
                SONG_LOCK.release()
            else:
                out_file = f"Songs\\{artist} {song}.ogg"

            if code == "REV" and out_file:
                SONG_LOCK.acquire()
                separate_song(artist, song)
                SONG_LOCK.release()
                out_file = f"SongsDetails\\{artist} {song}\\accompaniment.ogg"

            if out_file:
                # sends song file
                pickled_file = get_fileobject(out_file)

                print("File pickled")

                encryptor.send_msg(sock, pickled_file, "RES")

                # sends details
                if Path(f"SongsDetails\\{artist} {song}\\times.txt").is_file():
                    encryptor.send_msg(sock, "1", "SYC")
                    times = get_times(
                        f"SongsDetails\\{artist} {song}\\times.txt")
                    encryptor.send_msg(sock, times, "TIM")
                else:
                    if auto_sync:
                        SONG_LOCK.acquire()
                        if auto_sync_lyrics(artist, song):
                            encryptor.send_msg(sock, "1", "SYC")
                            times = get_times(
                                f"SongsDetails\\{artist} {song}\\times.txt")
                            encryptor.send_msg(sock, times, "TIM")
                        else:
                            encryptor.send_msg(sock, "0", "SYC")
                        SONG_LOCK.release()
                    else:
                        encryptor.send_msg(sock, "0", "SYC")

                lyrics = get_lyr(f"SongsDetails\\{artist} {song}\\lyrics.txt")
                encryptor.send_msg(sock, lyrics, "LYC")
            else:
                encryptor.send_msg(sock, "", "ERS")
                
            
            
        elif code == "EXT":
            return True


def handle_client(sock: socket.socket, id: int):
    print(f"started to handle client {id}")
    try:
        encryptor = encrypt_connection(sock)
        if not encryptor:
            raise Exception("Faild to Encrypt")

        print("Connected to client with", encryptor)

        if not login_register_loop(sock, encryptor):
            raise Exception("Login Ended")

        if not song_search_loop(sock, encryptor):
            raise Exception("Search Ended")

        print("Client disconnected from the server")

    except Exception as err:
        print(err)


def finish_threads():
    print("Started Close Thread")
    global threads,FINISH
    data = ""
    while data != "stop":
        data = input()
    FINISH = True


def main():
    global FINISH,DATA_BASE,PUB_KEY,PRIV_KEY

    DATA_BASE = DataBase()
    print("Connected to Data Base!")

    PUB_KEY,PRIV_KEY = encryption.generate_RSA_keys()
    print("RSA keys created!")

    sock = socket.socket()
    sock.settimeout(4.0)
    port = 12000

    sock.bind(('0.0.0.0', port))
    sock.listen(5)

    stop_th = threading.Thread(target=finish_threads)
    stop_th.start()
    
    threads = {}

    print("Waiting for clients!")

    i = 1

    while not FINISH:
        try:
            cli, addr = sock.accept()
            print(addr, "connected")
            t = threading.Thread(target=handle_client, args=[cli, i])
            t.start()
            threads[i] = [t, cli]
            i += 1
        except socket.timeout:
            pass
    
    
    for j in threads.keys():
        try:
            threads[j][1].close()
        except Exception:
            """Socket closed"""
        
        threads[j][0].join(timeout=0.2)
        
        if threads[j][0].is_alive():
            threads[j][0].daemon = True

        print(f"closed Socket and Thread of client {j}")
        
    
    stop_th.join()

if __name__ == '__main__':
    main()
