# Download CommonVoice Audio+Subtitle
This is the directory to download audio and subtitle from CommonVoice.
## Folder Structure
  ```
  raw_dataset/Commonvoice/
  │
  ├── cv-corpus-6.1/zh-TW/ - (files in Commonvoice dataset)
  │   ├── clips/ - all mp3 files
  |   |   └── xxx.mp3
  │   └──xxx.tsv - metadata tsv files
  │
  ├── wav/ -  (run 0_makeDataset.py)
  │   └── common_voice_zh-TW_xxx.wav
  │
  └── dataset/dataset.tsv - final dataset with text/path/mix (run 0_makeDataset.py)
  ```
## Usage
1. Download dataset from [download link](https://commonvoice.mozilla.org/)
    * Select version and language
    * Extract the ``LANGUAGE.tar`` file
2. Convert mp3 to wav and split into piece
```
python 0_makeDataset.py
```