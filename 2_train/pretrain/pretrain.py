import argparse
import os
from os.path import join as join_path
import torch
import multiprocessing
import sys

def main():
    
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument("--dataset_path", default=None, required=True, 
                        type=str, help="Path to unlabeled audio")
    
    parser.add_argument("--init_model", default=None, required=False,
                        type=str, help="Path to English pretrain wav2vec model")
    
    parser.add_argument("--mode_model", default='base', required=False,
                        type=str, help="base or large")
    
    parser.add_argument("--batch_size", default=1200000, required=False,
                        type=int,help="Batch size, try to decrease this number if any CUDA memory problems occur")
    
    args = parser.parse_args()
    
    
    #Pretrain the model
    NUM_GPU = torch.cuda.device_count()
    NUM_CPU = multiprocessing.cpu_count()
    
    if NUM_GPU == 0:
        print("pytorch cannot find any GPUs !")
        sys.exit(0)
    
    dir_path = os.path.realpath(args.dataset_path)
    cmd = ["fairseq-hydra-train"]
    cmd.append("task.data=" + str(dir_path))
    cmd.append("distributed_training.distributed_world_size=" + str(NUM_GPU))
    cmd.append("+optimization.update_freq='[" + str(int(64/NUM_GPU)) + "]'")
    
    if args.init_model != None:
        cmd.append("checkpoint.restore_file=" + os.path.abspath(args.init_model))
#         cmd.append("checkpoint.reset_optimizer=True")
#         cmd.append("checkpoint.reset_lr_scheduler=True")
#         cmd.append("checkpoint.reset_dataloader=True")
#         cmd.append("checkpoint.reset_meters=True")
    
    assert args.mode_model in ['base', 'large']
    if args.mode_model == 'base':
        config_name = 'wav2vec2_base_librispeech'
    elif args.mode_model == 'large':
        config_name = 'wav2vec2_large_librivox'

    
    #cmd.append("optimization.max_update=2000000")
    cmd.append("dataset.num_workers=" + str(NUM_CPU))
#     cmd.append("dataset.max_tokens=" + str(args.batch_size))
    cmd.append("--config-dir 2_train/wav2vec/config/pretraining")
    cmd.append("--config-name {}".format(str(config_name)))
    cmd = ' '.join(cmd)
    print(cmd)
    
    os.system(cmd)
    
main()