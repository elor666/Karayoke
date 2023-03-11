import customtkinter as tk
import pygame
from youtube_lyrics import search_result,download_song_lyrics
import os
import threading



SONG_PATH = ""

Song_Detail_Dir = "SongsDetails"
def create_song_dir(artist_name : str, song_name : str):
    global Song_Detail_Dir
    if not os.path.exists(f"{Song_Detail_Dir}\\{artist_name.lower()} {song_name.lower()}"):
        os.makedirs(f"{Song_Detail_Dir}\\{artist_name.lower()} {song_name.lower()}")

    Song_Detail_Dir = f"{Song_Detail_Dir}\\{artist_name.lower()} {song_name.lower()}"


class SyncApp(tk.CTk):
    def __init__(self):
        tk.set_appearance_mode("dark")
        #ctk.set_default_color_theme("dark-blue")
        tk.CTk.__init__(self)
        self.state("zoomed")#('-fullscreen', True)
        self.title("Music Player")
        #self.geometry('1980x1080')
        self._frame = None
        self.switch_frame(SearchPage)
        self.bind('<exit>',self.quit())

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
    
    
 

class SyncPage(tk.CTkFrame):
    def __init__(self,master):
        tk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        self.PAUSE = False
        self.STOP = True
        self.start = 0

        play_button = tk.CTkButton(self, text="Play", command=self.play_music)
        stop_button = tk.CTkButton(self, text="Stop", command=self.stop_music)
        pause_button = tk.CTkButton(self, text="Pause", command=self.pause_music)
        self.save_button = tk.CTkButton(self, text="Save", command=self.save,text_color_disabled="#A9A9A9")

        play_button.place(anchor='se',relx=0.53,rely=0.90,relwidth=0.025)
        stop_button.place(anchor='sw',relx=0.44,rely=0.90,relwidth=0.025)
        pause_button.place(anchor='sw',relx=0.47,rely=0.90,relwidth=0.025)
        self.save_button.place(anchor='se',relx=0.56,rely=0.90,relwidth=0.025)

        
        self.file_path = Song_Detail_Dir+"\\lyrics.txt"
        self.text_lines = []
        
        with open(self.file_path, 'r') as f:
            self.text_lines = f.readlines()
        
        self.text_lines = [l for l in self.text_lines if l != "\n"]
        self.times = ["0.0" for i in self.text_lines]
        self.playbuttons = [tk.CTkButton(self,command=lambda j=i: self.play_pos(j),text="play",width=28,height=28) for i in range(len(self.text_lines))]
        self.plusbuttons = [tk.CTkButton(self,command=lambda j=i: self.add_pos(j),text="+",width=28,height=28) for i in range(len(self.text_lines))]
        self.minusbuttons = [tk.CTkButton(self,command=lambda j=i: self.sub_pos(j),text="-",width=28,height=28) for i in range(len(self.text_lines))]
        self.index_line = 0
        
        self.labels = [[tk.CTkLabel(self, text=line,font=('Roboto',20)),tk.CTkLabel(self, text=self.times[i],font=('Roboto',20)),self.playbuttons[i],self.plusbuttons[i],self.minusbuttons[i]] for i,line in enumerate(self.text_lines[:5])]
        for i,(label1,label2,label3,l4,l5) in enumerate(self.labels):
            label2.place(anchor="ne",relx=0.45,rely=0.1*i+0.1)
            label1.place(anchor="nw",relx=0.5,rely=0.1*i+0.1)
            label3.place(anchor="n",relx=0.35,rely=0.1*i+0.1)
            l4.place(anchor="ne",relx=0.38,rely=0.1*i+0.1)
            l5.place(anchor="nw",relx=0.32,rely=0.1*i+0.1)
        
        self.slider = tk.CTkSlider(self, from_=len(self.text_lines) - 5, to=0, orientation="vertical", command=self.update_labels)
        self.slider.set(0)  #Scale
        self.slider.place(anchor="nw",relx="0",rely="0.1",relheight=0.5)
        
        self.save_label = tk.CTkLabel(self, text="to",font=('Roboto',20))
        self.save_label.place(anchor="center",relx=0.5,rely=0.75)

        self.bind("<MouseWheel>", self.mouse_scroll)
        master.bind("<Down>", self.move_line)

        pygame.mixer.init()

        sound = pygame.mixer.Sound(SONG_PATH)
        audio_length = sound.get_length()

        pygame.mixer.music.load(SONG_PATH)

        self.time_slider = tk.CTkSlider(self, from_=0, to=audio_length, orientation="horizontal", number_of_steps=round(audio_length//0.1)) #resolution=0.1
        self.time_slider.place(anchor="n",relx=0.5,rely=0.90,relwidth=0.7)

        self.after(100, self.update_slider)

    def play_music(self):
        self.STOP = False
        if not pygame.mixer.music.get_busy():
            if not self.PAUSE:
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()

    def play_pos(self,index):
        self.STOP = False
        if not pygame.mixer.get_busy():
            self.index_line = index
            index = float(self.times[index])
            if index != 0:
                self.start = index
                self.move_line(None)
                pygame.mixer.music.play(start=index)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.STOP = True
        self.PAUSE = False
        self.index_line = 0
        self.slider.set(0)
        self.update_labels(0)

    def pause_music(self):
        pygame.mixer.music.pause()
        self.PAUSE = True

    def save(self):
        self.save_button.configure(state='disable')
        with open(f"{Song_Detail_Dir}\\times.txt","w") as f:
            for line in self.times:
                f.write(line+"\n")
        self.save_button.configure(state='normal')
        self.save_label.configure(text="saved")

    def add_pos(self,index):
        self.times[index]=str(round(float(self.times[index])+0.01,3))
        if index >= 5:
            self.labels[index%5][1].configure(text=self.times[index])
        else:
            self.labels[index][1].configure(text=self.times[index])
        
        self.update_labels(self.slider.get())

    def sub_pos(self,index):
        self.times[index]=str(round(float(self.times[index])-0.01,3))
        if index >= 5:
            self.labels[index%5][1].configure(text=self.times[index])
        else:
            self.labels[index][1].configure(text=self.times[index])
        
        self.update_labels(self.slider.get())


    def update_slider(self):
        if not self.STOP:
            current_time = self.start + pygame.mixer.music.get_pos() / 1000
            self.time_slider.set(current_time)
        else:
            self.start = 0
            self.time_slider.set(0)
        self.after(100, self.update_slider)
    
    def update_labels(self, value):
        value = int(value)
        for i in range(5):
            self.labels[i][0].configure(text=self.text_lines[value + i])
            self.labels[i][1].configure(text=self.times[value + i])
            self.labels[i][2].configure(command = lambda j=value+i:self.play_pos(j))
            self.labels[i][3].configure(command = lambda j=value+i:self.add_pos(j))
            self.labels[i][4].configure(command = lambda j=value+i:self.sub_pos(j))
    
    def mouse_scroll(self, event):
        current_value = self.slider.get()
        if event.delta > 0:
            self.slider.set(current_value - 1)
            value = max(0,current_value - 1)
            self.update_labels(value)
        else:
            self.slider.set(current_value + 1)
            value = min(len(self.text_lines) - 5,current_value + 1)
            self.update_labels(value)
    
    def move_line(self,event):
        self.save_label.configure(text="")
        if self.index_line+1 <= len(self.times):
            if event != None:
                self.times[self.index_line]=str(round(self.start + pygame.mixer.music.get_pos() / 1000,3))
            if self.index_line >= len(self.text_lines) - 5:
                self.labels[self.index_line%(len(self.text_lines) - 5)][1].configure(text=self.times[self.index_line])
            else:
                self.labels[0][1].configure(text=self.times[self.index_line])
            self.slider.set(min(self.index_line,len(self.text_lines) - 5))
            self.update_labels(min(self.index_line,len(self.text_lines) - 5))
            self.index_line+=1

class SearchPage(tk.CTkFrame):
    def __init__(self, master):
        tk.CTkFrame.__init__(self, master)
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        self.artist_entry = tk.CTkEntry(self, placeholder_text="Artist", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        self.artist_entry.place(anchor='center', relx=0.2, rely=0.3)

        self.song_entry = tk.CTkEntry(self, placeholder_text="Song", width=280, height=56, placeholder_text_color="#C85C8E", font=("Roboto",21))
        self.song_entry.place(anchor='center', relx=0.2, rely=0.4)
        
        self.values = []
        self.choice = ""

        self.songs_menu = tk.CTkOptionMenu(self, values=[],command=self.optionmenu_callback,
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
        
        self.songs_menu.place(anchor="center", relx=0.2, rely=0.5)

        self.SEARCH = False
        self.search_button = tk.CTkButton(self,text="Search", fg_color="#9D3C72", width=56, height=56, hover_color="#C85C8E", command=lambda :self.get_search(),corner_radius=200,text_color="#FFBABA")
        self.search_button.place(anchor='e', relx=0.19, rely=0.6)

        self.CAN_SYNC = False
        self.sync_button = tk.CTkButton(self,text="Sync", fg_color="#808080", width=56, height=56, hover_color="#C85C8E", command=lambda :self.try_sync(master),corner_radius=200,text_color="#FFBABA",state="disabled")
        self.sync_button.place(anchor='w', relx=0.21, rely=0.6)

        self.labels = [tk.CTkLabel(self,text="", font=("Roboto",24), text_color="#FFBABA") for i in range(5)]

        for i,label in enumerate(self.labels):
            label.place(anchor='n', relx=0.7, rely=0.2+0.1*i)

    def optionmenu_callback(self,choice):
        print("optionmenu clicked:", choice)
        self.choice = choice
        self.enable_sync()
    

    def insert_results(self,result):
        for i,res in enumerate(result):
            self.labels[i].configure(text=res)
        
        if len(result)<len(self.labels):
            for i in range(len(result),len(self.labels)):
                self.labels[i].configure(text="")

    
    def get_search(self):
        self.disable_search()

        artist = self.artist_entry.get().lower()
        song = self.song_entry.get().lower()
        if artist != "" and song != "":
            result = search_result(artist,song)
            if result != []:
                if not f"{artist} {song}" in result:
                    #print(result)
                    self.values = result
                    self.songs_menu.configure(values=self.values)
                    self.insert_results(result)
                else:
                    [self.labels[i].configure(text="Can Sync") if i == 0 else self.labels[i].configure(text="") for i in range(len(self.labels))]
                    self.choice = ""

                    self.enable_sync()
            else:
                self.values = result
                self.songs_menu.configure(values=self.values)
                self.insert_results(result)
                self.disable_sync()
        self.enable_search()


    def end_sync(self,thread: threading.Thread,root):
        thread.join(timeout=0.2)
        if thread.is_alive():
            root.after(500,self.end_sync,thread,root)
        else:
            print("thread ended")
            self.enable_sync()
            self.enable_search()
            self.enable_menu()
            global SONG_PATH
            if SONG_PATH != "":
                root.switch_frame(SyncPage)

    def try_sync(self,root):
        self.disable_sync()
        self.disable_search()
        self.disable_menu()
        
        sync_thread = threading.Thread(target=self.get_sync)
        sync_thread.start()
        root.after(1500,self.end_sync,sync_thread,root)


    def get_sync(self):
        global SONG_PATH
        print("check if needs download")
        print("choice",self.choice)
        artist = self.artist_entry.get().lower()
        song = self.song_entry.get().lower()
        if self.choice != "":
            index = self.values.index(self.choice)
            download_song_lyrics(artist,song,int(index))
            create_song_dir(artist,song)
            SONG_PATH = "Songs\\"+artist.lower()+" "+song.lower()+".ogg"
        else:
            create_song_dir(artist,song)
            SONG_PATH = "Songs\\"+artist.lower()+" "+song.lower()+".ogg"

    def disable_search(self):
        self.search_button.configure(state="disabled",fg_color="#808080")

    def enable_search(self):
        self.search_button.configure(state="normal",fg_color="#9D3C72")

    def disable_sync(self):
        self.sync_button.configure(state="disabled",fg_color="#808080")

    def enable_sync(self):
        self.sync_button.configure(state="normal",fg_color="#9D3C72")

    def disable_menu(self):
        self.songs_menu.configure(state="disabled",button_color="#808080")

    def enable_menu(self):
        self.songs_menu.configure(state="normal",button_color="#7B2869")    
    

app = SyncApp()
app.mainloop()