import os
from pathlib import Path

from pydub import AudioSegment
from spleeter.separator import Separator

# ffmpeg -i test.mp4 test.wav
"""file that splits a song to vocal and else"""


def separate_song(artist, song):
    if not Path(f"SongsDetails\\{artist} {song}\\accompaniment.ogg").is_file() or\
    not Path(f"SongsDetails\\{artist} {song}" +"\\vocals.mp3").is_file():
        
        separator = Separator('spleeter:2stems')
        separator.separate_to_file(f"Songs\\{artist} {song}.ogg", f"SongsDetails", codec='ogg')

        audio_vocals = AudioSegment.from_file(
            f"SongsDetails\\{artist} {song}\\vocals.ogg")
        audio_vocals.export(
            f"SongsDetails\\{artist} {song}\\vocals.mp3",
            format="mp3")
        os.remove(f"SongsDetails\\{artist} {song}\\vocals.ogg")
