import os
from os.path import join as join_path
import multiprocessing
import sys
from collections import Counter
from tqdm import tqdm
from sklearn.utils import shuffle
import ntpath
import soundfile
import traceback

# Train: 1065191 | Valid: 56063...Press Enter
transcript_file = '1_dataset/finetune/training_dataset/transcript.txt'
save_dir = '1_dataset/finetune/training_dataset/'
n_process = 24
valid_percent = 0.05
train_size = 0
valid_size = 0
train_success = 0
valid_success = 0

sample_rate = 16000
max_sec = 200
max_frame_size = int(sample_rate * max_sec) 
min_sec = 0.5
min_frame_size = int(sample_rate * min_sec)

invalid_videos = set(['UCVDlbsa0hZqGTmUTPlPRvLw-4K0mVcdvLJY', 'UCJsq4QYu9BaxXDk0qR8Ms3w-E1ZiMHRn_ec', 'UC9i2Qgd5lizhVgJrdnxunKw-0LTkP7AHH3g', 'UCJsq4QYu9BaxXDk0qR8Ms3w-qBtS1UwEBH4', 'UCiWXd0nmBjlKROwzMyPV-Nw-I5kJLn7zqUg', 'UC959igjTLbgrZXCIoQwokwg-7nV0RhDIGCU', 'UCJsq4QYu9BaxXDk0qR8Ms3w-VL8omKA3Zfg', 'UCm2mMdP4_g5JmC4D-xXHJHg-k3NknhTrrg4', 'UCpgt8SEyAy5tbr9BzVK8Lsg-M7ero6xZeI8', 'UC959igjTLbgrZXCIoQwokwg-5e-5osUaQp4', 'UCUu9vTNP5b-RKxwlgAK170A-k3NknhTrrg4', 'UCJsq4QYu9BaxXDk0qR8Ms3w-odnL6blaiHI', 'UC959igjTLbgrZXCIoQwokwg-z-lbuE_deNs', 'UCpgt8SEyAy5tbr9BzVK8Lsg-60F8_hd_KLI', 'UCJsq4QYu9BaxXDk0qR8Ms3w-KXTu4leW2rw', 'UCJsq4QYu9BaxXDk0qR8Ms3w-MOZdE1BLLBA', 'UCulFhrW_YCwkq_BP16C82mA-yAFmQjpN7Jk', 'UC959igjTLbgrZXCIoQwokwg-vSsKZuNYVuM', 'UCVDlbsa0hZqGTmUTPlPRvLw-MNytZwCn10g', 'UCiWXd0nmBjlKROwzMyPV-Nw-KhNGsfOlJOY', 'UCJsq4QYu9BaxXDk0qR8Ms3w-STmasGqS_ys'])
# Create manifest files
train_all = os.path.join(save_dir,'train.all')
valid_all = os.path.join(save_dir, 'valid.all')
error_file = 'error.log'


def write_train_info(info):
    global train_success, train_size, n_process
    try:
        video_name = info['path'].split('/')[-1][:-9]

        if video_name not in invalid_videos:
            frames = soundfile.info(info['path']).frames
            if int(frames) < max_frame_size and int(frames) > min_frame_size:
                with open(train_all, 'a') as f:
                    f.write(f"{info['path']}\t{str(frames)}\t{info['word']}\t{info['letter']}\n")

    except Exception as e:
        with open(error_file, 'a') as error_log:
            error_log.write(f"Train: {info['path']}\n{e}\n{traceback.format_exc()}\n")
        
        
    train_success += 1
    print(f'[{train_success}/{train_size//n_process}]',end='\r')

def write_valid_info(info):
    global valid_success, valid_size, n_process
    try:
        video_name = info['path'].split('/')[-1][:-9]

        if video_name not in invalid_videos:    
            frames = soundfile.info(info['path']).frames
            if int(frames) < max_frame_size and int(frames) > min_frame_size:
                with open(valid_all, 'a') as f:
                    f.write(f"{info['path']}\t{str(frames)}\t{info['word']}\t{info['letter']}\n")
            
    except Exception as e:
        with open(error_file, 'a') as error_log:
            error_log.write(f"Valid: {info['path']}\n{e}\n{traceback.format_exc()}\n")
            
    valid_success += 1
    print(f'[{valid_success}/{valid_size//n_process}]',end='\r')
    
if __name__ == '__main__':
    with open(transcript_file) as f:
        data = f.read().splitlines()
    
    words = [d.split('\t')[1].upper() for d in data]
    letters = [d.replace(' ','|') for d in words]
    letters = [' '.join(list(d)) + ' |' for d in letters]
    paths = [d.split('\t')[0] for d in data]
    
    infos = [{
        'word': w,
        'letter': l,
        'path': p
    } for w,l,p in zip(words, letters, paths)]
    infos = shuffle(infos, random_state=42)    
    
    SPLIT_NUM = int(len(infos) * (1 - valid_percent))
    train_infos, valid_infos = infos[:SPLIT_NUM], infos[SPLIT_NUM:]
    train_size, valid_size = len(train_infos), len(valid_infos)
    input(f'Train: {train_size} | Valid: {valid_size}...Press Enter')
     
    pool = multiprocessing.Pool(processes=n_process)
    pool.map(write_train_info, train_infos)
    pool.map(write_valid_info, valid_infos)
    pool.close()
    pool.join()