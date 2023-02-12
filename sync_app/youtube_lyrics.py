from youtubesearchpython import VideosSearch
from pytube import YouTube
from pydub import AudioSegment
import os
from bs4 import BeautifulSoup
import requests
from pathlib import Path


def extract_lyrics(artist_name, song_name):
	#global artist, song
	link = 'https://www.azlyrics.com/lyrics/'+artist_name.replace(' ', '').lower()+'/'+song_name.replace(' ', '').lower()+".html"

	req = requests.get(link)
	#soup = BeautifulSoup(req.content, "html.parser")
	#find the lyrics
	#print(req.content)


	soup = BeautifulSoup(req.content.decode(),"html.parser")#make soup that is parse-able by bs
	so = set(soup.get_text().split("\n\n\n"))
	so = list(so)
	so.remove('')
  #print(s)
	lyrics = max(so, key=len)
	if lyrics == "Welcome to AZLyrics!\r\n              It's a place where all searches end!\r\n              We have a large, legal, every day growing universe of lyrics where stars of all genres and ages shine.":
		print("No Lyrics")
		return False
	else:
		#print(lyrics[2:])
		with open("lyrics.txt","w") as file:
			file.write(lyrics[2:])
		#print(len([i for i in lyrics[2:].split() if i!="\n"]))
		return True


def get_song_text(artist_name,song_name):
	"""if not downloaded yet, downloads the song if has lyrics for it, and retrive the lyrics\n
	song downloaded to {artist_name song_name.mp3} file in songs directory\n
	lyrics downloaded to {lyrics.txt} file in working directory"""

	if extract_lyrics(artist_name, song_name):
		if not Path(f"songs\\{artist_name} {song_name}.mp3").is_file():
			videosSearch = VideosSearch(f"{artist_name} {song_name}", limit = 2)

			r = (videosSearch.result())


			url = r["result"][0]["link"]
			
			#print(type(r["result"]))
			#for i in r["result"]:
				#print(i)
				#print("link",i["link"])



			#print(url)
			yt = YouTube(url)
			strem = yt.streams.filter(only_audio=True).desc()[0]
			out_file = strem.download("./songs")

			base, ext = os.path.splitext(out_file)
			new_file = r"./songs/"+f"{artist_name} {song_name}"+".mp3"
			AudioSegment.from_file(out_file).export(new_file, format="mp3")
			os.remove(out_file)
		return True
	else:
		return False

#get_song_text("stellar", "cold outside")

#print(new_file)
#print(strem)