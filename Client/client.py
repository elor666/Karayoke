import customtkinter as ctk
import threading
import socket
import encryption
import hashlib
import pickle
import base64
import pygame
from math import floor,ceil
import io
from io import BytesIO


Encryptor = None
SOCK = socket.socket()
SONG = None
LYRICS = None
TIMES = None
IS_SYNC = False
LINE_COUNT = 7


def time_format(ml_seconds):
    ml_seconds = int(ml_seconds)
    seconds, milliseconds = divmod(ml_seconds, 1000)
    minutes, seconds = divmod(seconds, 60)

    return f"{minutes:02d}:{seconds:02d}"


def equlize_words(sentence : str,limit=110):
    words = sentence.split()
    new_sentence = ""
    for word in words:
        if len(new_sentence.split("\n")[-1])+len(word)+1 > limit:
            new_sentence+='\n'+word
        else:
            new_sentence += " "+word

    return new_sentence[1:]




class App(ctk.CTk):
    def __init__(self):
        #ctk.set_appearance_mode("dark")
        #ctk.set_default_color_theme("dark-blue")
        ctk.CTk.__init__(self)
        self.attributes('-fullscreen', True)
        self._frame = None
        self.switch_frame(ConnectPage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame

class ConnectPage(ctk.CTkFrame):
    def __init__(self, master):
        global SOCK
        self.sock = SOCK


        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        title_label = ctk.CTkLabel(self,text="Karayoke", font=("Roboto",100), text_color="#7B2869")
        title_label.place(anchor='n', relx=0.5, rely=0.1)

        ip_entry = ctk.CTkEntry(self, placeholder_text="IP", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        ip_entry.place(anchor='center', relx=0.5, rely=0.3)
        

        port_entry = ctk.CTkEntry(self, placeholder_text="PORT", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        port_entry.place(anchor='center', relx=0.5, rely=0.4)

        #connect_func = partial(connect_server, root, ip_entry, port_entry)
        self.connect_button = ctk.CTkButton(self, command=lambda: self.connect_server(master,ip_entry,port_entry),
            text="Connect",
            fg_color="#7B2869",
            width=280,
            height=60,
            hover_color="#9D3C72")#"disabled"
            
        self.connect_button.place(anchor='n', relx=0.5, rely=0.5)

        #ctk.CTkButton(self, text="Open page one", command=lambda: master.switch_frame(PageOne)).place(anchor='n', relx=0.5, rely=0.5)
    
    def connect_server(self,root : ctk.CTk,ip_entry, port_entry):
            self.connect_button.configure(state=ctk.DISABLED, fg_color="#808080")
            ip = ip_entry.get()
            port = port_entry.get()
            
            if port.isdigit() and all(ch in "1234567890." for ch in ip):
                connection_thread = threading.Thread(target=self.try_connection, args=(ip, int(port)))
                connection_thread.start()
                root.after(2000, self.conclude_connection, root, connection_thread)
            else:
                print("Error")

    
    def conclude_connection(self,root, thread : threading.Thread):
        global Encryptor
        thread.join(timeout=0.2)

        if thread.is_alive():
            root.after(500,self.conclude_connection,root,thread)
        else:
            print("thread ended")
            self.connect_button.configure(state=ctk.NORMAL, fg_color="#7B2869")
            if Encryptor != None:
                print("connected to server with", Encryptor)
                root.switch_frame(LoginPage)
    

    def try_connection(self,ip : str, port : int):
        global Encryptor
        
        try:
            self.sock.connect((ip,port))

            len_msg = int(self.sock.recv(10))
            code = (self.sock.recv(3)).decode()
            if code == "PUB":
                pub = self.sock.recv(len_msg)

                Encryptor, rsa_num = encryption.generate_AESk_fpub(pub)

                len_msg = str(len(rsa_num)).zfill(10).encode()
                self.sock.send(len_msg+b'PUB'+rsa_num)
        except:
            print("Server not found")
            Encryptor = None


class LoginPage(ctk.CTkFrame):
    def __init__(self, master):
        self.LOGGED = False

        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        
        ctk.CTkLabel(self,text="Karayoke", font=("Roboto",100), text_color="#7B2869").place(anchor='n', relx=0.5, rely=0.1)


        self.user_entry = ctk.CTkEntry(self, placeholder_text="UserName", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        self.user_entry.place(anchor='center', relx=0.5, rely=0.3)
        self.user_entry.get()

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21),show="*")
        self.password_entry.place(anchor='center', relx=0.5, rely=0.4)
        self.password_entry.get()


        self.login_button = ctk.CTkButton(self,text="Login", fg_color="#7B2869", width=250, height=60, hover_color="#9D3C72",command=lambda: self.connect_server(master,self.user_entry,self.password_entry,"Login"))
        self.login_button.place(anchor='w', relx=0.51, rely=0.5)
        self.register_button = ctk.CTkButton(self,text="Register", fg_color="#7B2869", width=250, height=60, hover_color="#9D3C72",command=lambda: self.connect_server(master,self.user_entry,self.password_entry,"Register"))    
        self.register_button.place(anchor='e', relx=0.49, rely=0.5)

        #ctk.CTkLabel(self, text="This is page one").pack(side="top", fill="x", pady=10)
        #ctk.CTkButton(self, text="Return to start page",
        #          command=lambda: master.switch_frame(ConnectPage)).pack()
    
    
    def send_msg_tk(self,Encryptor : encryption.AESCipher,sock,msg,code):
        try:
            Encryptor.send_msg(sock,msg,code)
        except ConnectionResetError as err:
            self.quit()

    def connect_server(self,root,user_entry,password_entry,state):  
        user_entry.configure(state=ctk.DISABLED)
        password_entry.configure(state=ctk.DISABLED)
        
        password = password_entry.get()
        user = user_entry.get()
        if not password == "" and not user == "":
            password = hashlib.sha1(password.encode()).hexdigest()
                
            if all(ch not in "#" for ch in user):
                self.disable_buttons()
                connection_thread = threading.Thread(target=self.try_connection, args=(user, password,state))
                connection_thread.start()
                root.after(2000, self.conclude_connection, root, connection_thread)
            else:
                print('error')
        
        user_entry.configure(state=ctk.NORMAL)
        password_entry.configure(state=ctk.NORMAL)
    
    def try_connection(self,user, password, state):
        global Encryptor
        global SOCK

        if state == "Register":
            cod = "REG"
        else:
            cod = "LOG"
        self.send_msg_tk(Encryptor,SOCK,user+"#"+password,cod)

        code,msg = Encryptor.recieve_msg(SOCK)
        if code == "SUC":
            self.LOGGED = True
    
    def conclude_connection(self,root, thread : threading.Thread):
        thread.join(timeout=0.2)

        if thread.is_alive():
            root.after(1500,self.conclude_connection,root,thread)
        else:
            self.enable_buttons()
            print("thread ended")
            if self.LOGGED:
                print("Logged to server")
                root.switch_frame(SearchPage)

    def disable_buttons(self):
        self.login_button.configure(state="disabled", fg_color="#808080")
        self.register_button.configure(state="disabled", fg_color="#808080")
    
    def enable_buttons(self):
        self.login_button.configure(state="normal", fg_color="#7B2869")
        self.register_button.configure(state="normal", fg_color="#7B2869")



class SearchPage(ctk.CTkFrame):
    def __init__(self, master):
        self.FINISH = False

        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)

        title_label = ctk.CTkLabel(self,text="Karayoke", font=("Roboto",100), text_color="#7B2869")
        title_label.place(anchor='n', relx=0.5, rely=0.1)

        self.artist_entry = ctk.CTkEntry(self,placeholder_text="Artist name",placeholder_text_color="#C85C8E",width=280, height=56,font=("Roboto",21),text_color="#FFBABA")
        self.song_entry = ctk.CTkEntry(self,placeholder_text="Song name",placeholder_text_color="#C85C8E",width=280, height=56, font=("Roboto",21),text_color="#FFBABA")

        self.artist_entry.place(anchor='e', relx=0.495, rely=0.3)
        self.song_entry.place(anchor='w', relx=0.505, rely=0.3)

        self.SEARCH = False
        self.search_button = ctk.CTkButton(self,text="Search", fg_color="#9D3C72", width=56, height=56, hover_color="#C85C8E", command=lambda :self.get_search(master),corner_radius=200,text_color="#FFBABA")
        self.search_button.place(anchor='e', relx=0.445, rely=0.4)

        self.songs_menu = ctk.CTkOptionMenu(self, values=[],command=self.optionmenu_callback,
        fg_color="#7B2869", 
        button_color="#7B2869", 
        button_hover_color="#C85C8E", 
        dropdown_fg_color="#9D3C72", 
        dropdown_hover_color="#C85C8E", 
        width=250, 
        height=56, 
        dropdown_font=("Roboto",21), 
        text_color="#FFBABA")

        self.songs_menu.set("")
        
        self.songs_menu.place(anchor="w", relx=0.455, rely=0.4)

        self.no_vocals = ctk.BooleanVar(value=False)

        self.auto_sync = ctk.BooleanVar(value=False)

        self.vocals_check = ctk.CTkCheckBox(self,text="No Vocals", variable=self.no_vocals, onvalue=True, offvalue=False,
        checkmark_color="#FFBABA", fg_color="#7B2869",font=("Roboto",21),text_color="#C85C8E")

        self.vocals_check.place(anchor="center", relx=0.5, rely=0.5)

        self.auto_check = ctk.CTkCheckBox(self,text="Auto Sync", variable=self.auto_sync, onvalue=True, offvalue=False,
        checkmark_color="#FFBABA", fg_color="#7B2869",font=("Roboto",21),text_color="#C85C8E")

        self.auto_check.place(anchor="center", relx=0.5, rely=0.55)

        self.play_button = ctk.CTkButton(self,text="Play Song", fg_color="#7B2869", command=lambda :self.get_song_details(master),width=280, height=56,hover_color="#9D3C72",text_color="#FFBABA")
        self.play_button.place(anchor="center", relx=0.5, rely=0.6)

        self.choice = ""
        self.values = []
        
        self.exit_kar = ctk.CTkButton(self, text="Exit", command=self.exit_karyoke,fg_color="#7B2869",hover_color="#9D3C72")

        self.exit_kar.place(anchor="e",relx=0.95,rely=0.02)

    def send_msg_tk(self,Encryptor,sock,msg,code):
        try:
            Encryptor.send_msg(sock,msg,code)
        except ConnectionResetError as err:
            self.quit()
    
    
    def exit_karyoke(self):
        global SOCK,Encryptor
        self.send_msg_tk(Encryptor,SOCK,"","EXT")
        self.quit()

    def get_search(self,root):
            self.disable_buttons()
            self.songs_menu.set("")
            self.choice = ""
            self.songs_menu.configure(values="")
            self.values = []

            artist = self.artist_entry.get().lower()
            song = self.song_entry.get().lower()

            if all(ch not in "#" for ch in artist) and all(ch not in "#" for ch in song):
                self.send_msg_tk(Encryptor,SOCK,f"{artist}#{song}","SCH")
                search_thread = threading.Thread(target=self.get_lst_songs)
                search_thread.start()

                self.after(1500,self.try_end_search,search_thread,root)
    
    def try_end_search(self,search_thread,root):
        search_thread.join(timeout=0.2)

        if search_thread.is_alive():
            self.after(500,self.try_end_search,search_thread,root)
        else:
            self.enable_buttons()
            print("thread ended")
            if self.FINISH:
                if IS_SYNC:
                    root.switch_frame(KarayokePage)
                else:
                    root.switch_frame(KarayokePageNO)

    def get_lst_songs(self):
        code, msg = Encryptor.recieve_msg(SOCK)
        try:
            if code == "SCH":
                msg = base64.b64decode(msg)
                search_results = pickle.loads(msg)
                self.songs_menu.configure(values=search_results)
                self.values = search_results
            else:
                self.songs_menu.set("")
                self.choice = ""
                self.songs_menu.configure(values="")
                self.values = search_results
        except:
            print("Error")
        

    
    def optionmenu_callback(self,choice):
        self.choice = choice
    

    def get_song_details(self,root):
        self.disable_buttons()
        search_thread = threading.Thread(target=self.get_song)
        search_thread.start()

        self.after(1500,self.try_end_search,search_thread,root)
   

    def get_song(self):
        global SONG,LYRICS,TIMES,IS_SYNC
        msg_to_send = str(self.values.index(self.choice))+"#"+str(int(self.auto_sync.get()))
        if not self.no_vocals.get():
            self.send_msg_tk(Encryptor,SOCK,msg_to_send,"RES")
        else:
            self.send_msg_tk(Encryptor,SOCK,msg_to_send,"REV")
        try:
            code, msg = Encryptor.recieve_msg(SOCK)
            if code == "RES":
                msg = base64.b64decode(msg)
                SONG = pickle.loads(msg)
            else:
                raise Exception("ErrorRES")
            code, msg = Encryptor.recieve_msg(SOCK)
            if code == "SYC":
                if msg == b"1":
                    sync = True
                    code, msg = Encryptor.recieve_msg(SOCK)
                    if code == "TIM":
                        msg = base64.b64decode(msg)
                        TIMES = pickle.loads(msg) #List of times
                    else:
                        raise Exception("ErrorTIMES")
                else:
                    sync = False
                
                IS_SYNC = sync
            else:
                raise Exception("ErrorSYNC")

            code, msg = Encryptor.recieve_msg(SOCK)
            if code == "LYC":
                msg = base64.b64decode(msg)
                LYRICS = pickle.loads(msg) #List of lyrics
            else:
                raise Exception("ErrorLYRICS")
            
            self.FINISH = True
        except Exception as err:
            print(err)

    
    def disable_buttons(self):
        self.search_button.configure(state="disabled", fg_color="#808080")
        self.play_button.configure(state="disabled", fg_color="#808080")

    def enable_buttons(self):
        self.search_button.configure(state="normal", fg_color="#9D3C72")
        self.play_button.configure(state="normal", fg_color="#7B2869")


class KarayokePage(ctk.CTkFrame):
    def __init__(self, master):
        global SONG,LYRICS,TIMES,LINE_COUNT
        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)

        filee_copy = io.BytesIO(SONG.getvalue())

        pygame.mixer.init()
        pygame.mixer.music.load(SONG,'ogg')

        SONG.seek(0)

        self.text_lines = LYRICS
        self.text_lines = [equlize_words(line[:-1]) if line[-1]=='\n' else equlize_words(line) for line in self.text_lines if line != "\n"]

        self.times = TIMES

        self.scroll_index = 0

        self.labels = [ctk.CTkLabel(self,text_color="white" ,text=line,font=('Roboto',35)) for line in self.text_lines[:LINE_COUNT]]
        for i,label in enumerate(self.labels):
            label.place(anchor="w",relx=0.025,rely=0.1+0.11*i)
        

        self.play_button = ctk.CTkButton(self, text="Play", command=self.play_music,fg_color="#7B2869",hover_color="#9D3C72")
        self.pause_button = ctk.CTkButton(self, text="Pause", command=self.pause_music,fg_color="#7B2869",hover_color="#9D3C72")

        self.play_button.place(anchor='se',relx=0.53,rely=0.90,relwidth=0.025)
        self.pause_button.place(anchor='sw',relx=0.47,rely=0.90,relwidth=0.025)

        self.audio_length = pygame.mixer.Sound(filee_copy).get_length()

        self.time_slider = ctk.CTkSlider(self, from_=0, to=self.audio_length, orientation="horizontal",command=self.update_start,button_color="#7B2869",button_hover_color="#9D3C72")#, number_of_steps=round(audio_length//0.1)
        self.time_slider.set(pygame.mixer.music.get_pos())
        self.time_slider.place(anchor="n",relx=0.5,rely=0.90,relwidth=0.7)
        self.start = 0

        self.boldid = None
        self.update_id = None

        self.bind("<MouseWheel>", self.mouse_scroll)

        self.time_label = ctk.CTkLabel(self,text_color="white" ,text="0",font=('Roboto',25))
        self.time_label.place(anchor="n",relx=0.5,rely=0.915)
        
        self.back_button = ctk.CTkButton(self, text="Back", command=lambda: self.back(master),fg_color="#7B2869",hover_color="#9D3C72")

        self.back_button.place(anchor="e",relx=0.95,rely=0.02)    

        self.exit_kar = ctk.CTkButton(self, text="Exit", command=self.exit_karyoke,fg_color="#7B2869",hover_color="#9D3C72")

        self.exit_kar.place(anchor="e",relx=0.95,rely=0.07)

    def exit_karyoke(self):
        global SOCK,Encryptor
        self.pause_music()
        self.send_msg_tk(Encryptor,SOCK,"","EXT")
        self.quit()
    
    def back(self,master):
        self.pause_music()
        master.switch_frame(SearchPage)

    def mouse_scroll(self, event):
        if not pygame.mixer.music.get_busy():
            if event.delta > 0:
                #print("up")
                self.scroll_index = max(0,self.scroll_index - 1)
            else:
                self.scroll_index =min(len(self.times) - LINE_COUNT,self.scroll_index + 1)

            self.update_labels(index=self.scroll_index)


    def get_time_index(self,cur_time):
        """Return the index of the time un the times list"""
        if cur_time <= self.times[0]:
            return 0
        elif cur_time >= self.times[-1]:
            return len(self.times)-1
        for i in range(len(self.times)-1):
            if cur_time >= self.times[i] and cur_time < self.times[i+1]:
                return i
    
    def get_time_range(self,index,cur_time : float):
        if self.times[index]<=cur_time:
            return cur_time-self.times[index]
        elif self.times[-1]<cur_time:
            return 0
        else:
            return self.times[index]-cur_time

    def update_labels(self,index = None):
        if index==None:
            cur_time = self.time_slider.get()
            value = self.get_time_index(cur_time)
            self.scroll_index=value
        else:
            value = self.scroll_index

        if value>floor(LINE_COUNT/2) and value<=len(self.text_lines)-ceil(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[value-floor(LINE_COUNT/2) + i],text_color="white",font=('Roboto',35))
        elif value<=floor(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[i],text_color="white",font=('Roboto',35))
        elif value>len(self.text_lines)-ceil(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[len(self.text_lines)-LINE_COUNT+i],text_color="white",font=('Roboto',35))


        if index==None:
            self.bold_line(value)
            if value < len(self.text_lines)-1:
                if pygame.mixer.music.get_busy():
                    self.boldid = self.after((int((self.get_time_range(value+1,cur_time)))*1000),self.update_labels)
    
    def play_music(self):
        if not pygame.mixer.music.get_busy():
            cur_time = self.time_slider.get()
            index = self.get_time_index(cur_time)
            if index == 0:
                self.boldid = self.after(int(self.get_time_range(index,cur_time)*1000),self.update_labels)#int(self.get_time_range(self.get_time_index(cur_time),cur_time)*1000)
            else:
                self.boldid = self.after(0,self.update_labels)
            time = self.time_slider.get()
            if time<self.audio_length:
                pygame.mixer.music.play(start=time)
                self.update_id = self.after(0,self.update_slider,True)

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.after_cancel(self.update_id)
            self.update_slider(False)
            self.time_slider.set(self.start+pygame.mixer.music.get_pos()/1000)
            self.start = self.start+pygame.mixer.music.get_pos()/1000
            pygame.mixer.music.stop()
            self.after_cancel(self.boldid)

    def update_slider(self,again:bool):
        if pygame.mixer.music.get_busy():
            ml_time = pygame.mixer.music.get_pos()
            self.time_slider.set(self.start+ml_time/1000)

            ml_time += self.start*1000

            formatted_time = time_format(ml_time)

            self.time_label.configure(text=formatted_time)
        if again:
            self.update_id = self.after(100,self.update_slider,True)
    
    def update_start(self,value):
        if not pygame.mixer.music.get_busy():
            self.start = value
            ml_time = self.start*1000
            formatted_time = time_format(ml_time)
            self.time_label.configure(text=formatted_time)
            if not self.time_slider.get()<self.times[0]:
                self.update_labels()
            else:
                [label.configure(text_color="white",font=('Roboto',35)) for label in self.labels]

    def calculate_index(self,index):
        if index <=floor(LINE_COUNT/2):
            return index
        elif index >floor(LINE_COUNT/2) and index<len(self.text_lines)-floor(LINE_COUNT/2):
            return floor(LINE_COUNT/2)
        else:
            return LINE_COUNT-(len(self.text_lines)-index)

    def bold_line(self,index):
        """bold index of line in text_lines"""
        if index<len(self.text_lines):
            index = self.calculate_index(index)
            [label.configure(text_color="#FFBABA",font=('Roboto',35)) if i<index else label.configure(text_color="white",font=('Roboto',35)) for i,label in enumerate(self.labels)]
            self.labels[index].configure(text_color="#C85C8E",font=('Roboto',37))


class KarayokePageNO(ctk.CTkFrame):
    def __init__(self, master):
        global SONG,LYRICS,LINE_COUNT
        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        
        filee_copy = io.BytesIO(SONG.getvalue())

        pygame.mixer.init()
        pygame.mixer.music.load(SONG,'ogg')

        SONG.seek(0)

        self.text_lines = LYRICS
        self.text_lines = [equlize_words(line[:-1]) if line[-1]=='\n' else equlize_words(line) for line in self.text_lines if line != "\n"]
        
        self.labels = [ctk.CTkLabel(self,text_color="white" ,text=self.text_lines[i],font=('Roboto',35)) for i in range(LINE_COUNT)]
        for i,label in enumerate(self.labels):
            label.place(anchor="w",relx=0.025,rely=0.1+0.11*i)
        

        self.play_button = ctk.CTkButton(self, text="Play", command=self.play_music,fg_color="#7B2869",hover_color="#9D3C72")
        self.pause_button = ctk.CTkButton(self, text="Pause", command=self.pause_music,fg_color="#7B2869",hover_color="#9D3C72")

        self.play_button.place(anchor='se',relx=0.53,rely=0.90,relwidth=0.025)
        self.pause_button.place(anchor='sw',relx=0.47,rely=0.90,relwidth=0.025)

        self.audio_length = pygame.mixer.Sound(filee_copy).get_length()

        self.time_slider = ctk.CTkSlider(self, from_=0, to=self.audio_length, orientation="horizontal",command=self.update_start,button_color="#7B2869",button_hover_color="#9D3C72")#, number_of_steps=round(audio_length//0.1)
        self.time_slider.set(pygame.mixer.music.get_pos())
        self.time_slider.place(anchor="n",relx=0.5,rely=0.90,relwidth=0.7)
        self.start = 0

        self.update_id = None

        self.scroll_index = 0

        self.bind("<MouseWheel>", self.mouse_scroll)
        self.back_button = ctk.CTkButton(self, text="Back", command=lambda: self.back(master),fg_color="#7B2869",hover_color="#9D3C72")

        self.back_button.place(anchor="e",relx=0.95,rely=0.02)    

        self.exit_kar = ctk.CTkButton(self, text="Exit", command=self.exit_karyoke,fg_color="#7B2869",hover_color="#9D3C72")

        self.exit_kar.place(anchor="e",relx=0.95,rely=0.07)

    def exit_karyoke(self):
        global SOCK,Encryptor
        self.send_msg_tk(Encryptor,SOCK,"","EXT")
        self.quit()

    def back(self,master):
        self.pause_music()
        master.switch_frame(SearchPage)
        
        
    def update_start(self,value):
        if not pygame.mixer.music.get_busy():
            self.start = value

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.after_cancel(self.update_id)
            self.update_slider(False)
            self.time_slider.set(self.start+pygame.mixer.music.get_pos()/1000)
            self.start = self.start+pygame.mixer.music.get_pos()/1000
            pygame.mixer.music.stop()  

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            cur_time = self.time_slider.get()
            pygame.mixer.music.play(start=cur_time)
            self.update_id = self.after(0,self.update_slider,True)

    def update_slider(self,again: bool):
        if pygame.mixer.music.get_busy():
            self.time_slider.set(self.start+pygame.mixer.music.get_pos()/1000)
        if again:
            self.update_id = self.after(10,self.update_slider,True)
    

    def update_labels(self):
        value = self.scroll_index

        if value>floor(LINE_COUNT/2) and value<=len(self.text_lines)-ceil(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[value-floor(LINE_COUNT/2) + i],text_color="white",font=('Roboto',35))
        elif value<=floor(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[i],text_color="white",font=('Roboto',35))
        elif value>len(self.text_lines)-ceil(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[len(self.text_lines)-LINE_COUNT+i],text_color="white",font=('Roboto',35))



    def mouse_scroll(self, event):
        if event.delta > 0:
            self.scroll_index = max(0,self.scroll_index - 1)
        else:
            self.scroll_index =min(len(self.text_lines),self.scroll_index + 1)

        self.update_labels()

if __name__ == "__main__":
    app = App()
    app.mainloop()