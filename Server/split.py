from spleeter.separator import Separator
#ffmpeg -i test.mp4 test.wav
"""file that splits a song to vocal and else"""

def separate_song(artist,song):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(f"{artist} {song}.mp3", "SongsDetails")


#test
def main():
  separator = Separator('spleeter:2stems')
  separator.separate_to_file(f"stellar im still young.mp3", "SongsDetails")


if __name__ == "__main__":
  main()