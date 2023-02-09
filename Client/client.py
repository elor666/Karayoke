import customtkinter as ctk
import threading
import socket
import encryption
import hashlib


Encryptor = None
SOCK = socket.socket()

class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
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
        self.CONNECTING = False



        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        title_label = ctk.CTkLabel(self,text="Karayoke", font=("Roboto",100), text_color="#7B2869")
        title_label.place(anchor='n', relx=0.5, rely=0.1)

        ip_entry = ctk.CTkEntry(self, placeholder_text="IP", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        ip_entry.place(anchor='center', relx=0.5, rely=0.3)
        

        port_entry = ctk.CTkEntry(self, placeholder_text="PORT", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        port_entry.place(anchor='center', relx=0.5, rely=0.4)

        #connect_func = partial(connect_server, root, ip_entry, port_entry)
        connect_button = ctk.CTkButton(self, command=lambda: self.connect_server(master,ip_entry,port_entry), text="Connect", fg_color="#7B2869", width=280, height=60, hover_color="#9D3C72")
            
        connect_button.place(anchor='n', relx=0.5, rely=0.5)

        #ctk.CTkButton(self, text="Open page one", command=lambda: master.switch_frame(PageOne)).place(anchor='n', relx=0.5, rely=0.5)
    
    def connect_server(self,root : ctk.CTk,ip_entry, port_entry):
        if not self.CONNECTING:
            ip = "127.0.0.1" #ip_entry.get()
            port = "12000"#port_entry.get()
            
            if port.isdigit() and all(ch in "1234567890." for ch in ip):
                connection_thread = threading.Thread(target=self.try_connection, args=(ip, int(port)))
                connection_thread.start()
                root.after(2000, self.conclude_connection, root, connection_thread)
                print(ip, port)
            else:
                print("Error")
        else:
            print("wait for connection thread to finish")

    
    def conclude_connection(self,root, thread : threading.Thread):
        global Encryptor
        thread.join(timeout=0.2)

        if thread.is_alive():
            root.after(1500,self.conclude_connection,root,thread)
        else:
            print("thread ended")
            if Encryptor != None:
                print("connected to server with", Encryptor)
                root.switch_frame(LoginPage)
    

    def try_connection(self,ip : str, port : int):
        global Encryptor
        
        self.CONNECTING = True
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
        
        self.CONNECTING = False


class LoginPage(ctk.CTkFrame):
    def __init__(self, master):
        self.CONNECTING = False
        self.LOGGED = False

        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        
        ctk.CTkLabel(self,text="Karayoke", font=("Roboto",100), text_color="#7B2869").place(anchor='n', relx=0.5, rely=0.1)


        self.user_entry = ctk.CTkEntry(self, placeholder_text="UserName", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        self.user_entry.place(anchor='center', relx=0.5, rely=0.3)
        

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21),show="*")
        self.password_entry.place(anchor='center', relx=0.5, rely=0.4)

        login_button = ctk.CTkButton(self,text="Login", fg_color="#7B2869", width=250, height=60, hover_color="#9D3C72",command=lambda: self.connect_server(master,self.user_entry,self.password_entry,"Login")).place(anchor='w', relx=0.51, rely=0.5)
        register_button = ctk.CTkButton(self,text="Register", fg_color="#7B2869", width=250, height=60, hover_color="#9D3C72",command=lambda: self.connect_server(master,self.user_entry,self.password_entry,"Register")).place(anchor='e', relx=0.49, rely=0.5)    

        #ctk.CTkLabel(self, text="This is page one").pack(side="top", fill="x", pady=10)
        #ctk.CTkButton(self, text="Return to start page",
        #          command=lambda: master.switch_frame(ConnectPage)).pack()
    

    def connect_server(self,root,user_entry,password_entry,state):
        if not self.CONNECTING:
            
            user_entry.configure(state=ctk.DISABLED)
            password_entry.configure(state=ctk.DISABLED)
            
            user = user_entry.get()
            password = hashlib.sha1(password_entry.get().encode()).hexdigest()
            
            if all(ch not in "#" for ch in user):
                connection_thread = threading.Thread(target=self.try_connection, args=(user, password,state))
                connection_thread.start()
                root.after(2000, self.conclude_connection, root, connection_thread)
            else:
                print('error')

        else:
            print("wait for connection thread to finish")
        
        user_entry.configure(state=ctk.NORMAL)
        password_entry.configure(state=ctk.NORMAL)
    
    def try_connection(self,user, password, state):
        global Encryptor
        global SOCK

        self.CONNECTING = True
        if state == "Register":
            cod = "REG"
        else:
            cod = "LOG"
        Encryptor.send_msg(SOCK,user+"#"+password,cod)

        code,msg = Encryptor.recieve_msg(SOCK)
        if code == "SUC":
            self.LOGGED = True

        self.CONNECTING = False
    
    def conclude_connection(self,root, thread : threading.Thread):
        thread.join(timeout=0.2)

        if thread.is_alive():
            root.after(1500,self.conclude_connection,root,thread)
        else:
            print("thread ended")
            if self.LOGGED:
                print("connected to server with")
                root.switch_frame(HomePage)


class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        self.CONNECTING = False
        self.LOGGED = False

        ctk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)


if __name__ == "__main__":
    app = App()
    app.mainloop()