import argparse
import glob, os
import torch
from asr import ASRtranscribe


def main(args):
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    ASR = ASRtranscribe(
        w2v_path=args.w2v_path,
        dict_path=args.dict_path,
        vad_path=args.vad_path,
        device=device)
    
    files = list(glob.glob(os.path.join(args.sample_dir, "*.wav")))

    for f in files:
        print(ASR(f))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample_dir", default='inference/sample/', required=True, 
                       type=str, help="Path to sample wav")
    parser.add_argument("--w2v_path", default='inference/models/wav2vec.pt', required=True, 
                       type=str, help="Path to wav2vec model")
    parser.add_argument("--dict_path", default='inference/models/ltr.txt', required=True, 
                       type=str, help="Path to word dict file")
    parser.add_argument("--vad_path", default='inference/models/vad.pt', required=True, 
                       type=str, help="Path to vad model")
    args = parser.parse_args()
    main(args)