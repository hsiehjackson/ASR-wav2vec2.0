# Download Apple Podcast Audio
This is the directory to download audio from apple podcast.
## Folder Structure
  ```
  raw_dataset/Podcast/
  │
  ├── html/ - channel htmls
  |   ├── channelID.html
  │   └── idxxx.html
  │
  ├── mp3/ - episiode mp3/mp4 (run 0_download.py)
  │   ├── channelID-episodeID.mp3/mp4
  │   └── idxxx-1000xxx.mp3
  │
  ├── metadata/ - metadata for filename/title/url  (run 0_download.py)
  │   ├── metadata.json
  │   └── metadata.tsv
  │
  ├── wav/ - episode-piece wav (run 1_convert.py)
  │   ├── channelID/
  │   |   └── episodeID/
  │   |       └── channelID-episodeID-pieceID.wav
  │   └── idxxx/
  │       └── 1000xxx/
  │           └── idxxx-1000xxx-000.wav
  │
  ├── vad.py - python file to split wav intp piece
  │
  └── error.log - mp3/mp4 download failure records (run 0_download.py)
  ```
## Usage
1. Download podcast channel html
![](https://i.imgur.com/LWrr2WQ.gif)
    * Go to someone's apple podcast channel page
    (region in **tw** https://podcasts.apple.com/tw/podcast/)
    * Scroll down and show all the episodes
    * Save the html of the page
2. Move all channel xxx.html files to folder ``html/``
3. Download episode mp3/mp4
```
python 0_download.py
```
4. Convert mp3 to wav and split into piece
```
python 1_convert.py
```