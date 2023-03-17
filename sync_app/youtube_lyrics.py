from youtubesearchpython import VideosSearch
from pytube import YouTube
from pydub import AudioSegment
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from io import BytesIO
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import tempfile

Num_Search = 5
Max_duration = 420 #7 minutes long


def download_wait(directory, timeout):
    """
    Wait for downloads to finish with a specified timeout.
    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    time.sleep(3)

def download_youtube(url:str,directory:str):
  """youtube download"""
  url = "https://www.ss"+url[12:]

  option = Options()
  option.add_argument("--disable-extensions")
  #option.add_argument("--start-maximized")
  option.add_experimental_option(
      "prefs", {"profile.default_content_setting_values.notifications": 2,"profile.default_content_settings.popups": 0,"download.default_directory" : directory}
  )

  driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=option)
  driver.get(url)
  driver.minimize_window()
  time.sleep(7)

  driver.find_element(By.CSS_SELECTOR,'[class="link link-download subname ga_track_events download-icon"]').click()

  time.sleep(2)

  try:
    w1 = driver.window_handles[0]
    w2 = driver.window_handles[1]
    driver.switch_to.window(window_name=w2)
    driver.close()
    driver.switch_to.window(w1)
    driver.minimize_window()
  except:
      pass
  download_wait(directory,240)

  print("finished")

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
                if str(err)=="'NoneType' object has no attribute 'span'":
                    print("Youtube changed their api. No support for pytube.")

                    temp = tempfile.TemporaryDirectory()
                    download_youtube(url,temp.name)
                    fpath = f"{temp.name}\\{os.listdir(temp.name)[0]}"
                    AudioSegment.from_file(fpath).export(r"Songs/"+f"{artist_name} {song_name}"+".ogg",format="ogg")
                    os.remove(fpath)
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
#print(download_song_lyrics("elley duh","money on the dash",0))
#print(new_file)
#print(strem)