import whisper
from pydub import AudioSegment,silence
import os
from pathlib import Path
from spleeter.separator import Separator
import string
import contextlib


def split_song(artist_name,song_name):
    path = f"SongsDetails\\{artist_name} {song_name}"
    if not Path(path+"\\accompaniment.ogg").is_file() or not Path(path+"\\vocals.mp3").is_file():
        with contextlib.redirect_stdout(None):
            separator = Separator('spleeter:2stems')
        separator.separate_to_file(f"Songs\\{artist_name} {song_name}.ogg", "SongsDetails",codec="mp3")
        AudioSegment.from_file(path+f"\\accompaniment.mp3").export(path+f"\\accompaniment.ogg",format="ogg")
        os.remove(path+f"\\accompaniment.mp3")

def merge_dup(times,sentences):
    merged_sentences = []
    i = 0
    while i < len(times):
        current_time = times[i]
        current_sentence = sentences[i]
        j = i + 1
        while j < len(times) and times[j] == current_time:
            current_sentence += " " + sentences[j]
            j += 1
        merged_sentences.append(current_sentence.lower())
        i = j
    return merged_sentences


def jaccard_similarity(sent1, sent2):
    """Find text similarity using jaccard similarity"""
    # Tokenize sentences
    token1 = set(sent1.split())
    token2 = set(sent2.split())
     
    # intersection between tokens of two sentences    
    intersection_tokens = token1.intersection(token2)
    
    # Union between tokens of two sentences
    union_tokens=token1.union(token2)
    
    sim= float(len(intersection_tokens) / len(union_tokens))
    miss = len(sent1.split())-len(sent2.split())
    miss = miss if miss > 0 else 0
    return sim,miss

def get_segments(vocal_filename, model_size="medium"):
    with contextlib.redirect_stdout(None):
        model = whisper.load_model(model_size)
        result = model.transcribe(vocal_filename)
    #print(f"Segments: {len(result['segments'])}")
    return result['segments']

def sync_segments(lyrics, segments):
    lyrics_synced = []
    #lyrics_unsynced = lyrics.split('\n')
    lyrics = lyrics.replace("\n"," ")
    lyrics_unsynced = lyrics.split()

    for segment in segments:
        top_similarity = 0.0
        top_similarity_final_index = 1
        
        for i in range(1, len(lyrics_unsynced)):
            trial_text = ' '.join(lyrics_unsynced[:i])
            trial_similarity = jaccard_similarity(trial_text, segment['text'])
            if trial_similarity > top_similarity:
                top_similarity = trial_similarity
                top_similarity_final_index = i
        #lyrics_synced = lyrics_synced + list(map(lambda x: f"[{math.floor(segment['start']/60):02d}:{math.floor(segment['start'] % 60):02d}.00] {x}\n", lyrics_unsynced[:top_similarity_final_index]))
        lyrics_synced = lyrics_synced + list(map(lambda x: [int(segment['start']),str(x)], lyrics_unsynced[:top_similarity_final_index]))
        lyrics_unsynced = lyrics_unsynced[top_similarity_final_index:]

        
    #lyrics_synced = lyrics_synced + list(map(lambda x: f"[{math.floor(segments[-1]['start']/60):02d}:{math.floor(segments[-1]['start'] % 60):02d}.00] {x}\n", lyrics_unsynced[0:]))
    lyrics_synced = lyrics_synced + list(map(lambda x: [int(segments[-1]['start']),str(x)], lyrics_unsynced[0:]))
        
    return lyrics_synced


def sync_segments_fix(lyrics_full, segments):
    lyrics = lyrics_full.lower()
    lyrics = lyrics.replace("\n"," ")
    lyrics_full = lyrics_full.replace("\n"," ")
    lyrics_full = lyrics_full.split()
    lyrics_full = [ly.replace(" ","").strip() for ly in lyrics_full if ly not in string.punctuation]
    
    lyrics = lyrics.translate(str.maketrans('','',string.punctuation))

    lyrics = lyrics.split()

    sentences = [se["text"].replace("\n","").lower().strip().translate(str.maketrans('','',string.punctuation)) for se in segments]


    times = [round(float(se["start"]),2) for se in segments]

    finale_lyrics = []

    i = 0
    miss_of_top = 0
    window_index = 0
    for sentence in sentences:
        top_match_index = 0
        top_match_sim = -1
        if i!=len(lyrics)-1:
            for k in range(miss_of_top+1):
                for j in range(i+k+1,len(lyrics)):
                    temp_sentence = " ".join(lyrics[i+k:j])
                    sim,miss = jaccard_similarity(sentence,temp_sentence)

                    if sim> top_match_sim:
                        top_match_sim = sim
                        top_match_index = j
                        miss_of_top = miss
                        window_index = k
        else:
            top_match_index = i
            window_index=0
        
        if len(finale_lyrics) != 0:
            finale_lyrics[-1]= (finale_lyrics[-1]+" "+" ".join(lyrics_full[i:i+window_index])).strip()
        finale_lyrics.append(" ".join(lyrics_full[i+window_index:top_match_index]))
        i = top_match_index

    if i<len(lyrics):
        finale_lyrics[-1] =(finale_lyrics[-1]+" "+" ".join(lyrics_full[i:])).strip()
    

    return [(times[index],finale_lyrics[index]) for index in range(len(finale_lyrics))]

def detect_start(noise_time,path : str):
    """noise_time in seconds"""

    # Load the audio file
    audio = AudioSegment.from_file(path+r"\vocals.mp3", format="mp3")
    chunks = silence.detect_silence(audio[:(noise_time+1)*1000],silence_thresh=audio.dBFS-7)
    try:
        return round(chunks[0][1]/1000,2)
    except:
        return 0


def auto_sync_lyrics(artist, song):

    split_song(artist, song)

    segments = get_segments(f"SongsDetails\\{artist} {song}\\vocals.mp3")


    with open(f"SongsDetails\\{artist} {song}\\lyrics.txt", 'r') as f:
        full_lyrics = f.read()

    length_of_lyrics = len(full_lyrics)

    data = sync_segments_fix(full_lyrics, segments)

    times = [time for time,_ in data]

    lyrics = [sentence for _,sentence in data]

    lyrics = merge_dup(times,lyrics)

    if len(lyrics)/length_of_lyrics>0.01 and len([True for line in lyrics if len(line.split("\n"))<3])==0:
        times = sorted(list(set(times)))

        times[0] = detect_start(times[1],f"SongsDetails\\{artist} {song}")
        times = [str(t)+'\n' for t in times]
        lyrics = [ly.strip()+'\n' for ly in lyrics]

        with open(f"SongsDetails\\{artist} {song}\\times.txt",'w') as f:
            f.writelines(times)
        
        with open(f"SongsDetails\\{artist} {song}\\lyrics.txt",'w') as f:
            f.writelines(lyrics)
        
        return True
    
    return False


"""if __name__ == '__main__':
    auto_sync_lyrics("kid laroi", "stay")#("ed sheeran","shape of you")"""





