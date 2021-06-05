# Automatic speech recognition (wav2vec2.0)
In this project, you will go through the whole pipeline in ASR, such as data preparation, wav2vec2.0 pretraining, CTC finetuning, streaming inference, etc.

---
## Annoucement
* The project is focus on speech of Mandarian in Taiwan (**zh-TW**).
* When installing wav2letter, you may add ```"-DCMAKE_CXX_FLAGS=-I/usr/local/opt/openblas/include"``` in ```cmake_args``` in ```wav2letter/bindings/python/setup.py```
* My checkpoint is in [here](https://drive.google.com/drive/folders/1kgSMr4lBwvPbj9HspN0KfDLxWPITFbOE?usp=sharing). You can put files into `ckpt` folder.
---
## Install Requirements
* Create your own conda environment
```
conda create --name ASR python=3.6
```
* Install Package (conda/pip, torch, fairseq, apex, wav2letter...)
```
bash 0_install.sh
```
---
## Data Preparation
> Pretrain Dataset from Apple podcast `Audio`
* Go to ```1_dataset/pretrain/raw_dataset/Podcast```
* Follow ```README.md``` instructions
> Finetune Dataset from CommonVoice `Audio+Text`
* Go to ```1_dataset/finetune/raw_dataset/CommonVoice```
* Follow ```README.md``` instructions
> Finetune Dataset from Youtube `Audio+Text`
* Go to ```1_dataset/finetune/raw_dataset/Youtube```
* Follow ```README.md``` instructions
---
## Modeling - wav2vec2.0 Pretraining
> Start training
```
bash 1_pretrain.sh
```
* Create train dataset in following folder
```
1_dataset/pretrain/training_dataset/
├──train.tsv
└──valid.tsv
```
* Use Fairseq library to train model 
    * modify config file - ```2_train/wav2vec/config/pretraining```
    * add pretrain English ckpt as init_model - [link](https://github.com/pytorch/fairseq/blob/master/examples/wav2vec/README.md)
> View logs
```
outputs/
└── 2021/05/21
    └──19-00-00
        ├──checkpoints
        └──hydra_train.log
```
* Open hydra_train.log to view details
* Plot loss and acc
```
python plot/plot_pretrain.py --log_path=PATH/TO/hydra_train.log
```
![](https://i.imgur.com/X3RZZJ2.png)

---
## Modeling - CTC Finetuning
> Prepare pretrain ckpt
* Prepare pretrain wav2vec2.0 checkpoint in ckpt folder
```
ckpt/
└──pretrain.pt
```
> Start training
```
bash 2_finetune.sh
```
* Create train dataset in following folder
```
1_dataset/finetune/training_dataset/
├──transcript.txt - wavpath and text
├──dict.ltr.txt - letter info
├──train/valid.all - wavpath, frame_size, word, letter
├──train/valid.tsv - wavpath, frame_size
├──train/valid.ltr - word
└──train/valid.wrd - letter
```
* Use Fairseq library to train model 
    * modifiy config file - ```2_train/wav2vec/config/finetune```
    * add pretrain our/your ckpt as pretrain_model - 
> View logs
```
outputs/
└── 2021/05/21
    └──19-00-00
        ├──checkpoints
        └──hydra_train.log
```
* Open hydra_train.log to view details
* Plot loss and wer
```
python plot/plot_finetune.py --log_path=PATH/TO/hydra_train.log
```
![](https://i.imgur.com/6nokU85.png)

---
## Inference - File
> Prepare model and sample
```
ckpt/
├── pretrain.pt
├── finetune.pt
└── dict.ltr.txt

3_inference/sample/
├── 0.wav
├── 1.wav
└── xxx.wav
```
* Move your pretrain ckpt to ```ckpt/pretrain.pt```
* Move your finetune ckpt to ```ckpt/finetune.pt```
* Move your train_dataset letter info to```ckpt/dict.ltr.txt```
* Move your wav file to ```3_inference/sample```
> Start inference
```
bash 3_inference.sh
```
* Install stable fairseq==0.10.2
* Convert two model to single model
```
3_inference/models/
├── wav2vec.pt - final model for ASR
├── dict.ltr.txt - letter for text lookup
└── vad.pt - model for voice activity detection
```
* Inference Results
```
{'audio': '3_inference/sample/0.wav', 'duration': '0:00:02.784000', 'results': [{'speech_section': '0:00:00 ~ 0:00:03', 'length_ms': 2780.0, 'speech': '這世界充滿了正義與邪惡'}]}
{'audio': '3_inference/sample/1.wav', 'duration': '0:00:04.824000', 'results': [{'speech_section': '0:00:00 ~ 0:00:05', 'length_ms': 4820.0, 'speech': '希望來的是能夠作決定的人'}]}
```
---
## Inference - Streaming
> Start inference
```
bash 4_stream.sh
```
* Use PyAudio to open microphone
* It is still on development!!!
* Inference Results
```
Start Microphone...
你好
你好棒
...
```
---
## Reference
* [pytorch/fairseq](https://github.com/pytorch/fairseq)
* [kakaobrain/pororo](https://github.com/kakaobrain/pororo)
* [mailong25/self-supervised-speech-recognition](https://github.com/mailong25/self-supervised-speech-recognition)