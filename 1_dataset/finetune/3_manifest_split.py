import pandas as pd
import os

save_dir = '1_dataset/finetune/training_dataset'

##############
train_all = os.path.join(save_dir, 'train.all')
train_tsv = os.path.join(save_dir, 'train.tsv')
train_word = os.path.join(save_dir, 'train.wrd')
train_letter = os.path.join(save_dir, 'train.ltr')

with open(train_all) as f:
    all_lines = f.read().splitlines()

with open(train_tsv, 'w') as t, open(train_word, 'w') as w, open(train_letter, 'w') as l:
    t.write('\n')
    for line in all_lines:
        path,frame,word,letter = line.split('\t') 
        t.write(f"{path}\t{frame}\n")
        w.write(f"{word}\n")
        l.write(f"{letter}\n")

##############
valid_all = os.path.join(save_dir, 'valid.all')
valid_tsv = os.path.join(save_dir, 'valid.tsv')
valid_word = os.path.join(save_dir, 'valid.wrd')
valid_letter = os.path.join(save_dir, 'valid.ltr')

with open(valid_all) as f:
    all_lines = f.read().splitlines()


with open(valid_tsv, 'w') as t, open(valid_word, 'w') as w, open(valid_letter, 'w') as l:
    t.write('\n')
    for line in all_lines:
        path,frame,word,letter = line.split('\t') 
        t.write(f"{path}\t{frame}\n")
        w.write(f"{word}\n")
        l.write(f"{letter}\n")