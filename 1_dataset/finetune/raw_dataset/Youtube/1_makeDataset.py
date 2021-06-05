import os
import subprocess
import pandas as pd
import multiprocessing
import concurrent.futures 
import traceback

global_path2Youtube = os.path.realpath('.')
mp3_dir = os.path.join(global_path2Youtube, 'mp3')
tsv_dir = os.path.join(global_path2Youtube, 'subtitle')
wav_dir = os.path.join(global_path2Youtube, 'wav')
meta_dir = os.path.join(global_path2Youtube, 'metadata')
dataset_dir = os.path.join(global_path2Youtube, 'dataset')
error_file = os.path.join(global_path2Youtube, 'error.log')

os.makedirs(dataset_dir, exist_ok=True)
os.makedirs(wav_dir, exist_ok=True)
n_processes = 24
n_sucess = 0
total_files = 0

def process_split(sample):
    i, start, end, text, user_id, video_id, mp3file = sample
    wavfile = os.path.join(wav_dir, user_id, video_id, f'{user_id}-{video_id}-{i:04}.wav')
    if not os.path.isfile(wavfile):
        info = {
            'input': mp3file,
            'output': wavfile,
            'start': start,
            'end': end,
            'text': text
        }
        try:
            convert_and_split(info)
        except Exception as e:
            with open(error_file, 'a') as error_log:
                error_log.write(f'{wavfile}\n{e}\n{traceback.format_exc()}\n')
    else:
        with open(os.path.join(dataset_dir, 'dataset.tsv'), 'a') as f:
            f.write(f"{text}\t{wavfile}\tNone\n")

def process_mp3(sample):
    global n_sucess, total_files
    
    mp3, tsv = sample
    user_id, video_id = mp3[:24], mp3[25:-4]
    os.makedirs(os.path.join(wav_dir,user_id), exist_ok=True)
    os.makedirs(os.path.join(wav_dir,user_id,video_id), exist_ok=True)

    mp3file = os.path.join(mp3_dir, mp3)
    tsvfile = os.path.join(tsv_dir, tsv)
    df = pd.read_csv(tsvfile, sep='\t')
    samples = [[i, d[0], d[1], d[2], user_id, video_id, mp3file] for i, d in enumerate(df[['Start', 'End', 'Subtitle']].values.tolist())]
    
    with concurrent.futures.ThreadPoolExecutor() as exector: 
        exector.map(process_split, samples)

    n_sucess += 1
    print(f'[{n_sucess}/{total_files}] - [{len(df)}]')
            
def convert_and_split(info):    
    with open(error_file, "a") as f:
        subprocess.run(["ffmpeg", 
                        "-loglevel", "panic", 
                        "-i", info['input'],
                        "-ss", info['start'],
                        "-to", info['end'],
                        "-ac", "1",
                        "-ar", "16000", 
                        "-f", "wav", info['output']],
                        stdout=subprocess.DEVNULL,
                        stderr=f)

    with open(os.path.join(dataset_dir, 'dataset.tsv'), 'a') as f:
        f.write(f"{info['text']}\t{info['output']}\tNone\n")
        

if __name__ == '__main__':
    df = pd.read_csv(os.path.join(meta_dir, 'metadata.tsv'), sep='\t')
    samples = [[d[0], d[1]] for d in df[['mp3Path', 'subtitlePath']].values.tolist()]

    total_files = len(samples)
    input(f'Total: {total_files}...Press Enter')
    
    if not os.path.isfile(os.path.join(dataset_dir, 'dataset.tsv')):
        with open(os.path.join(dataset_dir, 'dataset.tsv'), 'w') as f:
            f.write('text\tpath\tmix\n')
    
    pool = multiprocessing.Pool(processes=n_processes)
    pool.map(process_mp3, samples)