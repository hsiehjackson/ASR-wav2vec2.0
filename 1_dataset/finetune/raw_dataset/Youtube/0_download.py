import os
import re
import json
import glob
from tqdm import tqdm
import pandas as pd
import urllib
import urllib.request
import urllib.parse as urlparse
import xml.etree.ElementTree as ET
from subtitle import YoutubeSubDownloader
import youtube_dl

import concurrent.futures 


mp3_folder = 'mp3'
subtitle_folder = 'subtitle'
metadata_folder = 'metadata'
error_file = 'error.log'
files = 0
total_file = 0

def get_video_urls(fname):
    f = open(fname, 'r').read()
    videos = re.findall(r'title="[^"]+?" href="https://www.youtube.com/watch\?v=.+?"', f)
    infos = []
    pbar = tqdm(videos)
    for v in pbar:
        v = re.sub(r'title=|href=|\"', r'',v)
        video_title, video_url = re.sub(r' https', r'\thttps',v).split('\t')
        video_id = urlparse.parse_qs(urlparse.urlparse(video_url).query)['v'][0]
        if 'zh-TW' in get_languages(video_id):
            infos.append({
                'url': video_url,
                'vid': video_id,
                'title': video_title
            })
            pbar.set_postfix({'zh-TW': len(infos)})
    return infos

def download_mp3_subtitile(url, filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': os.path.join(mp3_folder, '{}.%(ext)s'.format(filename)),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    downloader = YoutubeSubDownloader(url)
    downloader.download(language='zh-TW', folder=subtitle_folder, filename=filename)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def get_languages(video_id):
    url = "http://www.youtube.com/api/timedtext?v=%s&type=list" % video_id
    xml = urllib.request.urlopen(url)
    tree = ET.parse(xml)
    root = tree.getroot()
    languages = {}
    for child in root:
        languages[child.attrib["lang_code"]] = child.attrib["lang_translated"]
    return languages


def download_sample(info):
    global files, total_file
    uid = info[0]
    vid = info[1]
    url = info[2]
    title = info[3]

    title = title.replace('/','-')
    fileName = f'{uid}-{vid}'
    
    print(f'[{files}/{total_file}]Download...{fileName}')
    try:
        download_mp3_subtitile(url, fileName)
        mp3_path = os.path.join(mp3_folder, f'{fileName}.mp3')
        subtitle_path = os.path.join(subtitle_folder, f'{fileName}.tsv')
        if os.path.isfile(mp3_path) and os.path.isfile(subtitle_path):
            with open(os.path.join(metadata_folder, 'metadata.tsv'), 'a') as f: 
                f.write(f'{fileName}.mp3\t{fileName}.tsv\t{url}\t{title}\t{uid}\t{vid}\n')

    except Exception as e:
        with open(error_file, 'a') as error_log:
            error_log.write(f'{fileName}\t{e}\n')
    files += 1    

if __name__ == '__main__':
    CONCURRENT = True

    if not os.path.exists(mp3_folder):
        os.makedirs(mp3_folder, exist_ok=True)
    if not os.path.exists(subtitle_folder):
        os.makedirs(subtitle_folder, exist_ok=True)
    if not os.path.exists(metadata_folder):
        os.makedirs(metadata_folder, exist_ok=True)

    data = []
    for fname in list(glob.glob(os.path.join("html", "*.html"))):
        uid = fname.split('/')[-1][:-5]
        infos = get_video_urls(fname)
        for info in infos:
            data.append([uid, info['vid'], info['url'], info['title']])

    with open(os.path.join(metadata_folder, 'metavideo.tsv'), 'w') as f:
        df = pd.DataFrame(data, columns=['uid','vid','url','title'])
        df.to_csv(f, sep='\t', index=False)

    data = pd.read_csv(os.path.join(metadata_folder, 'metavideo.tsv'), sep='\t').values.tolist()
    total_file = len(data)
    input(f'Get {total_file} videos, press Enter...')
    
    if not os.path.isfile(os.path.join(metadata_folder, 'metadata.tsv')):
        with open(os.path.join(metadata_folder, 'metadata.tsv'), 'w') as f:
            f.write('mp3Path\tsubtitlePath\turl\ttitle\tuid\tvid\n')

    if CONCURRENT:
        print('Use Concurrent')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as exector: 
            exector.map(download_sample, data)
    else:
        for uid, vid, url, title in data:
            title = title.replace('/','-')
            fileName = f'{uid}-{vid}'
            
            if not os.path.isfile(os.path.join(subtitle_folder, f'{fileName}.tsv')):
                print(f'[{files}/{total_file}]Download...{fileName}')
                try:
                    download_mp3_subtitile(url, fileName)
                    mp3_path = os.path.join(mp3_folder, f'{fileName}.mp3')
                    subtitle_path = os.path.join(subtitle_folder, f'{fileName}.tsv')
                    if os.path.isfile(mp3_path) and os.path.isfile(subtitle_path):
                        with open(os.path.join(metadata_folder, 'metadata.tsv'), 'a') as f: 
                            f.write(f'{fileName}.mp3\t{fileName}.tsv\t{url}\t{title}\t{uid}\t{vid}\n')

                except Exception as e:
                    with open(error_file, 'a') as error_log:
                        error_log.write(f'{fileName}\t{e}\n')
            else:
                print(files, end='\r')

            files += 1
