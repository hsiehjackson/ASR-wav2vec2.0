# Download Youtube Audio+Subtitle
This is the directory to download audio and subtitle from youtube.
## Folder Structure
  ```
  raw_dataset/Youtube/
  │
  ├── html/ - channel htmls
  |   ├── channelID.html
  │   └── UCxxx.html
  │
  ├── mp3/ - video mp3 (run 0_download.py)
  │   ├── channelID-videoID.mp3
  │   └── UCxxx-xxx.mp3
  │
  ├── subtitle/ - video subtitle(run 0_download.py)
  │   ├── channelID-videoID.tsv
  │   └── UCxxx-xxx.tsv
  │
  ├── metadata/ - metadata for filename/title/url  (run 0_download.py)
  │   ├── metavideo.tsv
  │   └── metadata.tsv
  │
  ├── wav/ - episode-piece wav (run 1_makeDataset.py)
  │   ├── channelID/
  │   |   └── videoID/
  │   |       └── channelID-videoID-pieceID.wav
  │   └── UCxxx/
  │       └── xxx/
  │           └── UCxxx-xxx-000.wav
  │
  ├── dataset/dataset.tsv - final dataset with text/path/mix (run 1_makeDataset.py)
  │
  ├── subtitle.py - python file to dowload subtitle
  │
  └── error.log - mp3/subtitle download failure records (run 0_download.py)
  ```
## Usage
1. Download youtube channel html
![](https://i.imgur.com/FZtWPVe.gif)
    * Go to someone's youtube channel page (with subtitle)
    * Scroll down and show all the videos
    * Save the html of the page
2. Move all channel xxx.html files to folder ``html/``
3. Download episode mp3/subtitle
```
python 0_download.py
```
4. Convert mp3 to wav and split into piece
```
python 1_makeDataset.py
```