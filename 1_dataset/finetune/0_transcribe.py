import os
import re
import pandas as pd
from tqdm import tqdm
from clean import clean, rm_special, find_engWord

root_dir = '1_dataset/finetune/raw_dataset'
dataset_folder = os.listdir(root_dir)
dataset_folder = [os.path.join(root_dir,f) for f in dataset_folder if os.path.isdir(os.path.join(root_dir,f))]
data = []
for f in dataset_folder:
    data += pd.read_csv(os.path.join(f, 'dataset', 'dataset.tsv'), sep='\t').values.tolist()

input(f'Total Size: {len(data)}...Press Enter')


english = 0
clean_data = []
for idx, d in enumerate(data):
    text, path, mix = d[0], d[1], d[2]
    if not find_engWord(text):
        clean_text = clean(text)
        print(f'[{idx}/{len(data)}]{text} -> {clean_text}')
        if len(clean_text) > 0:
            clean_data.append(f'{path}\t{clean_text}')
    else:
        english += 1

print(f'Total Size: {len(data)}')
print(f'Clean Size:', len(clean_data))
print(f'English Size:', english)

with open('1_dataset/finetune/training_dataset/transcript.txt', 'w') as f:
    for d in clean_data:
        f.write(d)
        f.write('\n')
        
    

