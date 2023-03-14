from spleeter.separator import Separator
from enum import Enum
import os
from pathlib import Path
import os

class Codec(str, Enum):
    """Enumeration of supported audio codec."""

    WAV: str = "wav"
    MP3: str = "mp3"
    OGG: str = "ogg"
    M4A: str = "m4a"
    WMA: str = "wma"
    FLAC: str = "flac"

#ffmpeg -i test.mp4 test.wav
"""file that splits a song to vocal and else"""


def separate_song(path,artist,song):
    if not Path(f"SongsDetails\\{artist} {song}\\accompaniment.ogg").is_file():
      separator = Separator('spleeter:2stems')
      separator.separate_to_file(path, "SongsDetails",codec='ogg')
      os.remove(f"SongsDetails\\{artist} {song}\\voacls.ogg")

#test
def main():
  separator = Separator('spleeter:2stems')
  separator.separate_to_file(f"Songs\\elley duh money on the dash.ogg", "SongsDetails",codec='ogg')


if __name__ == "__main__":
  main()