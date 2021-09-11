import random
import subprocess
import glob


def get_audio():
    audio_files = glob.glob('stream/music/*.mp3')
    rdm_file = random.choice(audio_files)
    duration = subprocess.check_output(
        f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1\
                "{rdm_file}"',
        shell=True)
    dur = int(float(duration.decode('utf-8').replace('\n', '')))
    rdm_song = rdm_file.replace('stream/music/', '').replace('.mp3', '')
    song = ''
    with open('stream/song.txt', 'w') as f:
        c_per_line = 25
        if len(song) <= 25:
            song = rdm_song
        else:
            for i in range(len(rdm_song) % c_per_line):
                song += rdm_song[i*c_per_line:i*c_per_line+c_per_line] + '\n'
        f.write('Song - ' + song)
    return rdm_file, dur
