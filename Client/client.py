import customtkinter as ctk
from functools import partial
import threading
import socket


#connection vars
CONNECTED = False
SOCK = socket.socket()
CONNECTING = False
Encryptor = None


def conclude_connection(root, thread : threading.Thread):
  global CONNECTED
  thread.join(timeout=0.2)

  if thread.is_alive():
    root.after(2000,conclude_connection,root,thread)
  else:
    print("thread ended")
    if CONNECTED:
      pass



def try_connection(ip : str, port : int):
  global CONNECTING
  global SOCK
  global CONNECTED
  
  CONNECTING = True
  try:
    SOCK.connect((ip,port))
  except:
    print("Server not found")
    CONNECTED = False
  
  CONNECTING = False


def connect_server(root : ctk.CTk,ip_entry, port_entry):
  global CONNECTING

  if not CONNECTING:
    ip = ip_entry.get()
    port = port_entry.get()
    
    if port.isdigit() and all(ch in "1234567890." for ch in ip):
      connection_thread = threading.Thread(target=try_connection, args=(ip, int(port)))
      connection_thread.start()
      root.after(2000, conclude_connection, root, connection_thread)
      print(ip, port)
    else:
      print("Error")
  else:
    print("wait for connection thread to finish")


def connect_page(root):
  global CONNECTING
  
  frame = ctk.CTkFrame(root)
  frame.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)

  
  title_label = ctk.CTkLabel(frame,text="Karayoke", font=("Roboto",100), text_color="#7B2869")
  title_label.place(anchor='n', relx=0.5, rely=0.1)

  
  ip_entry = ctk.CTkEntry(frame, placeholder_text="IP", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
  ip_entry.place(anchor='center', relx=0.5, rely=0.3)
  

  port_entry = ctk.CTkEntry(frame, placeholder_text="PORT", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
  port_entry.place(anchor='center', relx=0.5, rely=0.4)


  connect_func = partial(connect_server, root, ip_entry, port_entry)
  connect_button = ctk.CTkButton(frame, command=connect_func, text="Connect", fg_color="#7B2869", width=280, height=60, hover_color="#9D3C72")
    
  connect_button.place(anchor='n', relx=0.5, rely=0.5)


def main():
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("dark-blue")
  root = ctk.CTk()
  root.attributes('-fullscreen', True)
  connect_page(root)

  root.mainloop()

if __name__ == '__main__':
  main()

