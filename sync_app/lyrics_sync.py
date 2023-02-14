import customtkinter as tk
import pygame
from youtube_lyrics import get_song_text
from pydub import AudioSegment
from io import BytesIO
import os




SONG_PATH = ""

Song_Detail_Dir = "SongsDetails"

def create_song_dir(artist_name : str, song_name : str):
    global Song_Detail_Dir
    if not os.path.exists(f"{Song_Detail_Dir}\\{artist_name.lower()} {song_name.lower()}"):
        os.makedirs(f"{Song_Detail_Dir}\\{artist_name.lower()} {song_name.lower()}")

    Song_Detail_Dir = f"{Song_Detail_Dir}\\{artist_name.lower()} {song_name.lower()}"
    

class App(tk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Music Player")
        self.geometry('1200x500')
        self.PAUSE = False
        self.STOP = True
        self.start = 0
        self.file_object = BytesIO()
        self.song = AudioSegment.from_mp3(SONG_PATH)

        play_button = tk.CTkButton(self, text="Play", command=self.play_music)
        stop_button = tk.CTkButton(self, text="Stop", command=self.stop_music)
        pause_button = tk.CTkButton(self, text="Pause", command=self.pause_music)
        save_button = tk.CTkButton(self, text="Save", command=self.save)

        play_button.place(anchor='se',relx=0.53,rely=0.90,relwidth=0.025)
        stop_button.place(anchor='sw',relx=0.44,rely=0.90,relwidth=0.025)
        pause_button.place(anchor='sw',relx=0.47,rely=0.90,relwidth=0.025)
        save_button.place(anchor='se',relx=0.56,rely=0.90,relwidth=0.025)

        
        self.file_path = "lyrics.txt"
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
        
        self.bind("<MouseWheel>", self.mouse_scroll)
        self.bind("<Down>", self.move_line)

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
                pygame.mixer.music.load(SONG_PATH)
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()

    def play_pos(self,index):
        self.STOP = False
        if not pygame.mixer.get_busy():
            self.index_line = index
            index = float(self.times[index])
            if index != 0:
                #pygame.mixer.music.set_pos(index)
                self.start = index
                self.move_line(None)
                #pygame.mixer.music.unload()
                self.write_temp(index)
                pygame.mixer.music.load(self.file_object,"mp3")
                pygame.mixer.music.play()

    def stop_music(self):
        pygame.mixer.music.unload()
        self.STOP = True
        self.PAUSE = False
        self.index_line = 0
        #self.time_slider.set(0)
        #pygame.mixer.music.play(start=0)
        self.slider.set(0)
        self.update_labels(0)

    def pause_music(self):
        pygame.mixer.music.pause()
        self.PAUSE = True

    def save(self):
        with open(f"{Song_Detail_Dir}\\times.txt","w") as f:
            for line in self.times:
                f.write(line+"\n")

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
    

    def write_temp(self,start):
        self.file_object = BytesIO()
        self.song[start*1000:].export(self.file_object,format="mp3")
        self.file_object.seek(0)



artist = "onerepublic"
song = "I aint worried"

if get_song_text(artist,song):
    create_song_dir(artist,song)
    SONG_PATH = "songs\\"+artist.lower()+" "+song.lower()+".mp3"

    app = App()
    app.mainloop()
