import argparse
import os
from os.path import join as join_path
import torch
import multiprocessing
import sys
import pandas as pd

def main():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--manifest_dir", default=None, required=True, 
                       type=str, help="Path to save manifest")
    
    parser.add_argument("--pretrain_model", default=None, required=True,
                        type=str, help="Path to pretrain wav2vec model")
    
    parser.add_argument("--batch_size", default=3200000, required=False,
                        type=int,help="Batch size, try to decrease this number if any CUDA memory problems occur")
    
    parser.add_argument("--restore_file", default=None, required=False,
                        type=str,help= "Resume training from fine-tuned checkpoint")
    
    args = parser.parse_args()
    
    args.pretrain_model = os.path.abspath(args.pretrain_model)
    args.manifest_dir = os.path.abspath(args.manifest_dir)
                        
    
    #Pretrain the model
    NUM_GPU = torch.cuda.device_count()
    NUM_CPU = multiprocessing.cpu_count() // 2
    print(f'Use GPU: {NUM_GPU}')
    print(f'Use CPU: {NUM_CPU}')
    
    if NUM_GPU == 0:
        print("pytorch cannot find any GPUs !")
        sys.exit(0)
    
        
    frames = [int(l[1]) for l in pd.read_csv(os.path.join(args.manifest_dir, 'train.tsv') ,sep='\t').values.tolist()]
    
    total_duration = sum(frames) / 16000
    total_duration = total_duration / 3600.0
    
    if total_duration <= 5:
        config_name = "base_1h"
    elif total_duration <= 50:
        config_name = "base_10h"
    elif total_duration <= 500:
        config_name = "base_100h"
    else:
        config_name = "base_960h"
        
    input(f'Total Duration {total_duration}h Use Config {config_name}...Press Enter')    
    
    cmd = ["fairseq-hydra-train"]
    cmd.append("task.data=" + str(args.manifest_dir))
    cmd.append("distributed_training.distributed_world_size=" + str(NUM_GPU))
    cmd.append("+optimization.update_freq='[" + str(int(8/NUM_GPU)) + "]'")
    cmd.append("model.w2v_path=" + args.pretrain_model)
    cmd.append("dataset.num_workers=" + str(NUM_CPU))
    cmd.append("dataset.max_tokens=" + str(args.batch_size))
    
    if args.restore_file is not None:
        cmd.append("checkpoint.restore_file=" + args.restore_file)
        #cmd.append("checkpoint.reset_optimizer=True")
        #cmd.append("checkpoint.reset_lr_scheduler=True")
        #cmd.append("checkpoint.reset_dataloader=True")
        #cmd.append("checkpoint.reset_meters=True")
    
    #cmd.append("optimization.max_update=100000")
    #cmd.append("dataset.validate_after_updates=0")
    #cmd.append("model.freeze_finetune_updates=0")
    cmd.append("--config-dir  2_train/wav2vec/config/finetuning")
    cmd.append("--config-name " + config_name)
    cmd = ' '.join(cmd)
    print(cmd)
    
    os.system(cmd)
    
main()
