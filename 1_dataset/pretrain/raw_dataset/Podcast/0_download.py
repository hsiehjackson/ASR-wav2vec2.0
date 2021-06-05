import os
import re
import glob
import json
import requests
import pandas as pd

html_folder = "html"
metadata_folder = "metadata"
mp3_folder = "mp3"
region = 'tw'

def get_episode_urls(fname, author_id):
    f = open(fname, 'r').read()
    ep_urls = re.findall(f'"https://podcasts.apple.com/{region}/podcast/.+?/{author_id}\?i=.+?"', f)
    ep_titles = re.findall(f'<a href="https://podcasts.apple.com/{region}/podcast/.+?/{author_id}\?i=.+?>.+?</a>', f.replace('\n',''))
    ep_urls = [h.replace('\"', '') for h in ep_urls]
    ep_ids = [u.split('i=')[-1] for u in ep_urls] 
    ep_titles = [t.split('>')[-2].replace('</a','').replace(' ','') for t in ep_titles]
    assert (len(ep_urls) == len(ep_titles)), print(fname, len(ep_urls), len(ep_titles))
    return ep_urls, ep_titles, ep_ids

def download_mp3(episode_url, fileName):
    r = requests.get(episode_url)
    r.raise_for_status()
    assert r.status_code == 200, print(f'[Error] {episode_url}')
    mp3_string = re.search(r'"assetUrl":".+?"', r.text)
    mp3_url = ':'.join(mp3_string.group(0).split(':')[1:]).replace('\"','')

    r = requests.get(mp3_url)
    r.raise_for_status()
    assert r.status_code == 200, print(f'[Error] {mp3_url}')

    isMp3 = re.search(r'\.mp3', mp3_url)
    isMp4 = re.search(r'\.m4a', mp3_url)

    if isMp4:
        save_path = os.path.join(mp3_folder, f'{fileName}.mp4')
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return f'{fileName}.mp4'  

    if isMp3:
        save_path = os.path.join(mp3_folder, f'{fileName}.mp3')
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return f'{fileName}.mp3'


if __name__ == '__main__':
    if not os.path.exists(html_folder):
        os.makedirs(html_folder, exist_ok=True)
    if not os.path.exists(metadata_folder):
        os.makedirs(metadata_folder, exist_ok=True)
    if not os.path.exists(mp3_folder):
        os.makedirs(mp3_folder, exist_ok=True)

    total_file = 0
    podcast_url = {}
    for fname in glob.glob(os.path.join(html_folder, "*.html")):
        author_id = fname.split('/')[-1][:-5]
        ep_urls, ep_titles, ep_ids = get_episode_urls(fname, author_id)
        podcast_url[author_id] = {
            'urls': ep_urls,
            'epID': ep_ids,
            'titles':ep_titles
        }
        total_file += len(ep_urls)

    json.dump(podcast_url, open(os.path.join(metadata_folder,'metadata.json'), 'w'),indent=4, ensure_ascii=False)
    input(f'Get {total_file} podcasts, press Enter...')

    files = 0
    writefile = []
    for author_id, v in podcast_url.items():
        for u, t, n in (zip(v['urls'], v['titles'], v['epID'])):
            t = t.replace('/','-')
            fileName = f'{author_id}-{n}'
            existMp3 = os.path.isfile(os.path.join(mp3_folder, f'{fileName}.mp3'))
            existMp4 = os.path.isfile(os.path.join(mp3_folder, f'{fileName}.mp4'))
            
            if existMp3:
                writefile.append([f'{fileName}.mp3', t, u])
            
            if existMp4:
                writefile.append([f'{fileName}.mp4', t, u])
            
            if (not existMp3) and (not existMp4):
                print(f'[{files+1}/{total_file}]Download...{fileName}')
                try:
                    fname = download_mp3(u, fileName)
                    writefile.append([fname, t, u])
                except Exception as e:
                    print(f'Error-[{files+1}/{total_file}]Download...{fileName}')
                    with open('error.log', 'a') as error_log:
                        error_log.write(f'{fileName} - {u} - {e}\n')
            files += 1
    
    df = pd.DataFrame(writefile,columns=['fileName', 'title', 'url'])
    with open(os.path.join(metadata_folder,'metadata.tsv'), 'w') as f:
        df.to_csv(f, index=False, sep='\t')
