import torch
import collections
import argparse
import json
import shutil

def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        
        new_key = parent_key if k == '_name' else k

        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretrain_path", required=True, 
                       type=str, help="Path to pretrain wav2vec")
    parser.add_argument("--finetune_path", required=True, 
                       type=str, help="Path to finetune wav2vecCTC")
    parser.add_argument("--dict_path", required=True, 
                       type=str, help="Path to manifest folder")
    args = parser.parse_args()
    
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p_ckpt = torch.load(args.pretrain_path, map_location=device)
    f_ckpt = torch.load(args.finetune_path, map_location=device)
    p_cfg = flatten(p_ckpt['cfg'])
    f_cfg = flatten(f_ckpt['cfg'])
    p_args = argparse.Namespace()
    f_args = argparse.Namespace()
    with open('3_inference/config/pretrain_args.json', 'r') as f:
        p_args.__dict__ = json.load(f)
    with open('3_inference/config/finetune_args.json', 'r') as f:
        f_args.__dict__ = json.load(f)


    for k, v in p_cfg.items():
        if k in p_args:
            setattr(p_args, k, v)

    for k, v in f_cfg.items():
        if k in f_args:
            setattr(f_args, k, v)
    
    setattr(p_args, 'latent_temp', str(tuple(p_args.latent_temp)))
    setattr(p_args, 'log_keys', str((p_args.log_keys)))

    f_ckpt['args'] = f_args
    f_ckpt['pretrain_args'] = p_args
    torch.save(f_ckpt, '3_inference/models/wav2vec.pt')
    
    
    shutil.copy(args.dict_path, '3_inference/models/dict.ltr.txt')