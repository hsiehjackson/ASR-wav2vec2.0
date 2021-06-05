import os
import glob
import multiprocessing
import pandas as pd
import subprocess


global_path2CommomVoice = os.path.realpath('.')
dir_path = os.path.join(global_path2CommomVoice, "cv-corpus-6.1/zh-TW")
wav_dir = os.path.join(global_path2CommomVoice, 'wav')
dataset_dir = os.path.join(global_path2CommomVoice, 'dataset')
os.makedirs(wav_dir, exist_ok=True)
os.makedirs(dataset_dir, exist_ok=True)

success = 0
n_process = 20

def convert_file(file):
    global success
    fname, sentence, up, down, total_size = file
    
    fname_wav = convert_type(fname)
    print(f'[{success:04}/{total_size // n_process} - {int(up) < int(down)}]', end='\r')

    success += 1
    return [sentence, fname_wav, int(up) < int(down)]
    
def convert_type(fname):        
    path_out_file = os.path.join(wav_dir, fname.split('/')[-1][:-3] + 'wav')
    if not os.path.isfile(path_out_file):
        subprocess.run(["ffmpeg", "-loglevel", "panic", "-i", fname,
                        "-ac", "1",
                        "-ar", "16000", 
                        "-f", "wav", path_out_file],
                        stdout=subprocess.DEVNULL)
    
    return path_out_file
    

if __name__ == '__main__':
    INVALIDATED = set('39cff2037cffdfa6c9d8fcd0875825c51c5c372b5d39936de41da2d46dfa1ff1357e3d7aa4b7809c750e21e3fac5e5e29500e928c3aa2ba39961e4c4bc49894a')
    tsv_val_path = os.path.join(dir_path, 'validated.tsv')
    tsv_other_path = os.path.join(dir_path, 'other.tsv')
    tsv_val_data = pd.read_csv(tsv_val_path, sep='\t')[['path', 'sentence', 'up_votes', 'down_votes', 'client_id']].values.tolist()
    tsv_other_data = pd.read_csv(tsv_other_path, sep='\t')[['path', 'sentence', 'up_votes', 'down_votes', 'client_id']].values.tolist()

    tsv_data = tsv_val_data + tsv_other_data
    tsv_data = [[os.path.join(dir_path, 'clips', d[0]), d[1], d[2], d[3],len(tsv_data)] for d in tsv_data if d[4] not in INVALIDATED]
    input(f'Size: {len(tsv_data)}...Press Enter')

    P = multiprocessing.Pool(processes=n_process)
    tsv_data_wav = P.map(convert_file, tsv_data)
    P.close()
    P.join()


    with open(os.path.join(dataset_dir,'dataset.tsv'),'w',encoding='utf-8',errors='ignore') as f:
        df = pd.DataFrame(tsv_data_wav,columns=['text', 'path', 'mix'])
        df.to_csv(f, index=False, sep='\t')