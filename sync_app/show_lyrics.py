import customtkinter as tk
import pygame
from math import floor,ceil

import pandas as pd

LINE_COUNT = 7
tk.set_appearance_mode("dark")


class TimedLyrics(tk.CTk):
    def __init__(self, file_path, *args, **kwargs):
        tk.CTk.__init__(self, *args, **kwargs)
        self.state("zoomed")
        self.file_path = file_path
        self.text_lines = []
        pygame.mixer.init()
        pygame.mixer.music.load("Songs\\"+file_path+".ogg")
        
        with open("SongsDetails\\"+self.file_path+"\\lyrics.txt", 'r') as f:
            self.text_lines = f.readlines()
        self.text_lines = [line[:-1] if line[-1]=='\n' else line for line in self.text_lines if line != "\n"]
        #print(self.text_lines)

        self.scroll_index = 0

        with open("SongsDetails\\"+self.file_path+"\\times.txt", 'r') as f:
            self.times = f.readlines()
        self.times = [float(time[:-1]) if time[-1]=='\n' else float(time) for time in self.times]

        self.labels = [tk.CTkLabel(self,text_color="white" ,text=line,font=('Roboto',40)) for line in self.text_lines[:LINE_COUNT]]
        for i,label in enumerate(self.labels):
            label.place(anchor="w",relx=0.1,rely=0.15+0.075*i)
        

        self.play_button = tk.CTkButton(self, text="Play", command=self.play_music,fg_color="#7B2869",hover_color="#9D3C72")
        self.pause_button = tk.CTkButton(self, text="Pause", command=self.pause_music,fg_color="#7B2869",hover_color="#9D3C72")

        self.play_button.place(anchor='se',relx=0.53,rely=0.90,relwidth=0.025)
        self.pause_button.place(anchor='sw',relx=0.47,rely=0.90,relwidth=0.025)

        self.audio_length = pygame.mixer.Sound("Songs\\"+file_path+".ogg").get_length()

        self.time_slider = tk.CTkSlider(self, from_=0, to=self.audio_length, orientation="horizontal",command=self.update_start,button_color="#7B2869",button_hover_color="#9D3C72")#, number_of_steps=round(audio_length//0.1)
        self.time_slider.set(pygame.mixer.music.get_pos())
        self.time_slider.place(anchor="n",relx=0.5,rely=0.90,relwidth=0.7)
        #print(self.time_slider.get(),audio_length)
        self.start = 0

        self.boldid = None
        #self.after_cancel(self.afterid)
        self.update_id = None

        self.bind("<MouseWheel>", self.mouse_scroll)

        self.time_label = tk.CTkLabel(self,text_color="white" ,text="0",font=('Roboto',25))
        self.time_label.place(anchor="n",relx=0.5,rely=0.915)
    
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
                self.labels[i].configure(text=self.text_lines[value-floor(LINE_COUNT/2) + i],text_color="white",font=('Roboto',40))
        elif value<=floor(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[i],text_color="white",font=('Roboto',40))
        elif value>len(self.text_lines)-ceil(LINE_COUNT/2):
            for i in range(LINE_COUNT):
                self.labels[i].configure(text=self.text_lines[len(self.text_lines)-LINE_COUNT+i],text_color="white",font=('Roboto',40))


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
            self.time_label.configure(text=pd.to_datetime(ml_time, unit='ms').strftime("%H:%M:%S"))
        if again:
            self.update_id = self.after(50,self.update_slider,True)
    
    def update_start(self,value):
        if not pygame.mixer.music.get_busy():
            self.start = value
            self.time_label.configure(text=pd.to_datetime(self.start*1000, unit='ms').strftime("%H:%M:%S"))
            if not self.time_slider.get()<self.times[0]:
                self.update_labels()
            else:
                [label.configure(text_color="white",font=('Roboto',40)) for label in self.labels]

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
            [label.configure(text_color="#FFBABA",font=('Roboto',40)) if i<index else label.configure(text_color="white",font=('Roboto',40)) for i,label in enumerate(self.labels)]
            self.labels[index].configure(text_color="#C85C8E",font=('Roboto',55))


class Lyrics(tk.CTk):
    def __init__(self, file_path, *args, **kwargs):
        tk.CTk.__init__(self, *args, **kwargs)
        self.state("zoomed")
        self.file_path = file_path
        pygame.mixer.init()
        pygame.mixer.music.load("Songs\\"+file_path+".ogg")
        
        with open("SongsDetails\\"+self.file_path+"\\lyrics.txt", 'r') as f:
            self.text_lines = f.readlines()
        self.text_lines = [line[:-1] if line[-1]=='\n' else line for line in self.text_lines if line != "\n"]


        self.label_frame = tk.CTkScrollableFrame(self,width=0.90*self.winfo_width(),height=0.8*self.winfo_height())
        self.label_frame.place(anchor="nw",relx=0.05,rely=0.01)
        self.labels = [tk.CTkLabel(self.label_frame,text_color="white" ,text=line,font=('Roboto',40)) for line in self.text_lines]
        for i,label in enumerate(self.labels):
            label.pack(anchor='w',pady=20,padx=10)
        

        self.play_button = tk.CTkButton(self, text="Play", command=self.play_music,fg_color="#7B2869",hover_color="#9D3C72")
        self.pause_button = tk.CTkButton(self, text="Pause", command=self.pause_music,fg_color="#7B2869",hover_color="#9D3C72")

        self.play_button.place(anchor='se',relx=0.53,rely=0.90,relwidth=0.025)
        self.pause_button.place(anchor='sw',relx=0.47,rely=0.90,relwidth=0.025)

        self.audio_length = pygame.mixer.Sound("Songs\\"+file_path+".ogg").get_length()

        self.time_slider = tk.CTkSlider(self, from_=0, to=self.audio_length, orientation="horizontal",command=self.update_start,button_color="#7B2869",button_hover_color="#9D3C72")#, number_of_steps=round(audio_length//0.1)
        self.time_slider.set(pygame.mixer.music.get_pos())
        self.time_slider.place(anchor="n",relx=0.5,rely=0.90,relwidth=0.7)
        self.start = 0

        self.update_id = None


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

if __name__ == "__main__":
    app = TimedLyrics(r"elley duh money on the dash")
    app.mainloop()