from youtubesearchpython import VideosSearch
from pytube import YouTube
from pydub import AudioSegment
import os
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from io import BytesIO

Num_Search = 5
Max_duration = 420 #7 minutes long


def extract_lyrics(artist_name, song_name):
    if not Path(f"SongsDetails\\{artist_name} {song_name}\\lyrics.txt").is_file():
        link = 'https://www.azlyrics.com/lyrics/'+artist_name.replace(' ', '').lower()+'/'+song_name.replace(' ', '').lower()+".html"

        req = requests.get(link)

        soup = BeautifulSoup(req.content.decode(),"html.parser")#make soup that is parse-able by bs
        so = set(soup.get_text().split("\n\n\n"))
        so = list(so)

        so.remove('')
        lyrics = max(so, key=len)
        if lyrics == "Welcome to AZLyrics!\r\n              It's a place where all searches end!\r\n              We have a large, legal, every day growing universe of lyrics where stars of all genres and ages shine.":
            print("Lyrics not found")
            return False
        #print(lyrics[2:])
        if not Path(f"SongsDetails//{artist_name.lower()} {song_name.lower()}").exists():
            os.makedirs(f"SongsDetails//{artist_name.lower()} {song_name.lower()}")
            
        with open(f"SongsDetails//{artist_name.lower()} {song_name.lower()}//lyrics.txt","w") as file:
            file.write(lyrics[2:])
        
        print("Got Lyrics")
    return True
    

def download_song_lyrics(artist_name, song_name, search_index):

    if extract_lyrics(artist_name, song_name):
        if not Path(f"Songs\\{artist_name} {song_name}.ogg").is_file():
            videosSearch = VideosSearch(f"{artist_name} {song_name}", limit = search_index+1)

            r = videosSearch.result()
            #print(r)
            #print(type(r["result"]))
            #for i in r["result"]:
                #print(i)
                #print("link",i["link"])
            r = [(r['result'][i]["link"],r['result'][i]["title"]) for i in range(len(r['result'])) if not str_time(r['result'][i]['duration']) > Max_duration]
            print(r)
            url = r[search_index][0]
            print(r[search_index][1])

            print(url)

            yt = YouTube(url)
            strem = yt.streams.filter(only_audio=True)[0]
            out_file = strem.download("./Songs")

            base, ext = os.path.splitext(out_file)
            new_file = r"Songs/"+f"{artist_name} {song_name}"+".ogg"
            AudioSegment.from_file(out_file).export(new_file, format="ogg")
            os.remove(out_file)
        
        return new_file
    
    return False

def str_time(timestr):
    ftr = [3600,60,1][-(len(timestr.split(":"))):3]
    #print(sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))]))
    return sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))])

def search_result(artist_name, song_name):
    if extract_lyrics(artist_name, song_name):
        if not Path(f"Songs\\{artist_name} {song_name}.ogg").is_file():
            videosSearch = VideosSearch(f"{artist_name} {song_name}", limit = Num_Search)
            res = videosSearch.result()
            return [res['result'][i]["title"]+" "+res['result'][i]['duration'] for i in range(len(res['result'])) if not str_time(res['result'][i]['duration']) > Max_duration]
        else:
            return [f"{artist_name} {song_name}"]
    return []

print("downloading")
data = BytesIO()
yt = YouTube("https://www.youtube.com/watch?v=JGwWNGJdvx8")
strem = yt.streams.filter(only_audio=True).asc()[0]
print(strem)
print("downloading")
out_file = strem.stream_to_buffer(data)
data.seek(0)
"""with open("temp.webm","wb") as f:
    f.write(data.read())"""
AudioSegment.from_file(data).export("temp.ogg",format="ogg")
print("exported")
#get_song_text("stellar", "cold outside")

#print(new_file)
#print(strem)