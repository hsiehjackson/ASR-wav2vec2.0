import os
import glob
import subprocess
import argparse
import multiprocessing

import webrtcvad
from vad import read_wave, write_wave, frame_generator, vad_collector


success = 0
n_process = 20
mp3_folder = "mp3"
wav_folder = "wav"

frame_duration_ms = 30
slide_window_duration_ms = 210
vad = webrtcvad.Vad(0)


def convert(n_processes=16):

    files = sorted(glob.glob(os.path.join(mp3_folder, "*.mp3")) + glob.glob(os.path.join(mp3_folder, "*.mp4")))
    print(f"{len(files)} files found")
    files = [(f, len(files)) for f in files]
    
    pool = multiprocessing.Pool(processes=n_processes)
    pool.map(convert_file, files)
    

def convert_file(file):
    global success
    fname, total_size = file
    
    segSize = convert_piece(convert_type(fname), total_size, success)
    print(f'[{success:04}/{total_size}] - Segments: {segSize}')
    
    success += 1


def convert_type(fname):    
    
    path_out_file = os.path.join(wav_folder, fname.split('/')[-1][:-3] + 'wav')
    

        
    subprocess.run(["ffmpeg", "-loglevel", "panic", "-i", fname,
                    "-ac", "1",
                    "-ar", "16000", 
                    "-f", "wav", path_out_file],
                    stdout=subprocess.DEVNULL)
    
    return path_out_file
    
    
def convert_piece(fname, total_size, success):
    user_id = fname.split('/')[-1].split('-')[0]
    ep_id = fname.split('/')[-1].split('-')[-1][:-4]
    chunk_folder = os.path.join(wav_folder, user_id, ep_id)
    
    if not os.path.exists(chunk_folder):
        os.makedirs(chunk_folder, exist_ok=True)
        

    audio, sample_rate = read_wave(fname)
    frames = frame_generator(frame_duration_ms, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, frame_duration_ms, slide_window_duration_ms, vad, frames)
    
    size = 0
    for segment in segments:
        path = os.path.join(chunk_folder, f'{user_id}-{ep_id}-{size:04}.wav')
        write_wave(path, segment, sample_rate)
        size += 1
        
        print(f'[{success:04}/{total_size // n_process}] - Segments: {size}', end='\r')
    
    os.remove(fname)

    return size

    
if __name__ == "__main__":
    
    if not os.path.exists(wav_folder):
        os.makedirs(wav_folder, exist_ok=True)

    convert()