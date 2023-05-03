import os
from enum import Enum
from pathlib import Path

from pydub import AudioSegment
from spleeter.separator import Separator


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

      audio_vocals = AudioSegment.from_file(f"SongsDetails\\{artist} {song}\\vocals.ogg")
      audio_vocals.export(f"SongsDetails\\{artist} {song}\\vocals.mp3",format="mp3")
      os.remove(f"SongsDetails\\{artist} {song}\\vocals.ogg")

#test
def main():
  separator = Separator('spleeter:2stems')
  separator.separate_to_file(f"Songs\\elley duh money on the dash.ogg", "SongsDetails",codec='ogg')


if __name__ == "__main__":
  main()