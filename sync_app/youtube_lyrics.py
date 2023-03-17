from youtubesearchpython import VideosSearch
from pytube import YouTube
from pydub import AudioSegment
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from io import BytesIO
import os
import webbrowser
import pyperclip
import subprocess
import tempfile

Num_Search = 5
Max_duration = 420 #7 minutes long


def extract_lyrics(artist_name, song_name):
    """downloads lyrics if have them on the site 'azlyrics.com' and if not downloaded yet."""

    if not Path(f"SongsDetails\\{artist_name} {song_name}\\lyrics.txt").is_file():
        link = 'https://www.azlyrics.com/lyrics/'+artist_name.replace(' ', '').lower()+'/'+song_name.replace(' ', '').lower()+".html"

        req = requests.get(link)

        soup = BeautifulSoup(req.content.decode(),"html.parser")

        temp_soup = soup.find("div",{"class":"col-xs-12 col-lg-8 text-center"})

        if temp_soup != None:
            lyrics = temp_soup.find("div",{"class":""}).get_text().strip()

            if lyrics != None:
                if not Path(f"SongsDetails//{artist_name.lower()} {song_name.lower()}").exists():
                    os.makedirs(f"SongsDetails//{artist_name.lower()} {song_name.lower()}")
                    
                with open(f"SongsDetails//{artist_name.lower()} {song_name.lower()}//lyrics.txt","w") as file:
                    file.write(lyrics)
        
                print("Got Lyrics")
                return True
        
        return False
    return True

def is_lyrics(artist_name, song_name):  
    """return whether lyrics exists or not"""
    if not Path(f"SongsDetails\\{artist_name} {song_name}\\lyrics.txt").is_file():
        
        link = 'https://www.azlyrics.com/lyrics/'+artist_name.replace(' ', '').lower()+'/'+song_name.replace(' ', '').lower()+".html"

        req = requests.get(link)

        soup = BeautifulSoup(req.content.decode(),"html.parser")

        temp_soup = soup.find("div",{"class":"col-xs-12 col-lg-8 text-center"})

        if temp_soup != None:
            lyrics = temp_soup.find("div",{"class":""}).get_text().strip()

            if lyrics != None:
                return True
    
        return False

    return True

def download_song_lyrics(artist_name, song_name, search_index):

    if extract_lyrics(artist_name, song_name):
        if not Path(f"Songs\\{artist_name} {song_name}.ogg").is_file():
            try:
                videosSearch = VideosSearch(f"{artist_name} {song_name}", limit = search_index+1)

                r = videosSearch.result()
                #print(r)
                #print(type(r["result"]))
                #for i in r["result"]:
                    #print(i)
                    #print("link",i["link"])
                url = r["result"][search_index]["link"]

                data = BytesIO()
                yt = YouTube(url)
                strem = yt.streams.filter(only_audio=True).asc()[0]
                strem.stream_to_buffer(data)
                data.seek(0)
                path_file = r"Songs/"+f"{artist_name} {song_name}"+".ogg"
                AudioSegment.from_file(data).export(path_file,format="ogg")
            
                return path_file
            except Exception as err:
                print("Youtube changed their api. No support for downloading automaticly.")
                webbrowser.open('https://en.savefrom.net/1-youtube-video-downloader-457/')

                pyperclip.copy(url)
                print(url,"has been copied to your clipboard")
                
                
                temp = tempfile.TemporaryDirectory()
                subprocess.Popen(f'explorer "{temp.name}"')

                finish = False
                while not finish:
                    input("press Enter to continue")
                    try:
                        fpath = f"{temp.name}\\"+[f for f in os.listdir(temp.name) if os.path.isfile(os.path.join(temp.name, f))][0]
                        AudioSegment.from_file(fpath).export(r"Songs/"+f"{artist_name} {song_name}"+".ogg",format="ogg")
                        os.remove(fpath)
                        finish = True
                    except Exception as err:
                        print(err)
                        print("follow the insturctions above and try again")
                
                temp.cleanup()
                return f"Songs\\{artist_name} {song_name}.ogg"

        return f"Songs\\{artist_name} {song_name}.ogg"
    
    return False

def str_time(timestr):
    """returns the number of seconds from a time string format H:M:S"""
    ftr = [3600,60,1][-(len(timestr.split(":"))):3]
    return sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))])

def search_result(artist_name, song_name):
    if is_lyrics(artist_name, song_name):
        if not Path(f"Songs\\{artist_name} {song_name}.ogg").is_file():
            videosSearch = VideosSearch(f"{artist_name} {song_name}", limit = Num_Search)
            res = videosSearch.result()
            return [res['result'][i]["title"]+" "+res['result'][i]['duration'] for i in range(len(res['result'])) if not str_time(res['result'][i]['duration']) > Max_duration]
        else:
            return [f"{artist_name} {song_name}"]
    return []

	

#get_song_text("stellar", "cold outside")
download_song_lyrics("stellar","bad dream",0)
#print(new_file)
#print(strem)