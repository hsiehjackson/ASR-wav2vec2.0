import json
import urllib
import urllib.parse as urlparse
import argparse
import sys
import xml.etree.ElementTree as ET
import os

class YoutubeSubDownloader(object):
    def __init__(self, url=None, video_id=None):
        self.video_id = self.extractVideoID(url)
        self.languages = self.getAvailableLanguages()
        assert 'zh-TW' in self.languages

    def extractVideoID(self, url=None):
        """
        Examples:
        - http://youtu.be/5MgBikgcWnY
        - http://www.youtube.com/watch?v=5MgBikgcWnY&feature=feed
        - http://www.youtube.com/embed/5MgBikgcWnY
        - http://www.youtube.com/v/5MgBikgcWnY?version=3&amp;hl=en_US
        """
        url_data = urlparse.urlparse(url)
        if url_data.hostname == 'youtu.be':
            return url_data.path[1:]
        if url_data.hostname in ('www.youtube.com', 'youtube.com'):
            if url_data.path == '/watch':
                query = urlparse.parse_qs(url_data.query)
                return query['v'][0]
            if url_data.path[:7] == '/embed/':
                return url_data.path.split('/')[2]
            if url_data.path[:3] == '/v/':
                return url_data.path.split('/')[2]
        return None

    def download(self, language, folder, filename):
        """Download subtitle of the selected language"""
        if language not in self.languages.keys():
            print("Theres's no subtitle in this language")
            sys.exit()
        url = "http://www.youtube.com/api/timedtext?v={0}&lang={1}".format(self.video_id, language)
        self.subtitle = urllib.request.urlopen(url)
        self.writeSRTFile(folder, filename)

    def getAvailableLanguages(self):
        """Get all available languages of subtitle"""
        url = "http://www.youtube.com/api/timedtext?v=%s&type=list" % self.video_id
        xml = urllib.request.urlopen(url)
        tree = ET.parse(xml)
        root = tree.getroot()
        languages = {}
        for child in root:
            languages[child.attrib["lang_code"]] = child.attrib["lang_translated"]
        return languages
    

    def list(self):
        """List all available languages of subtitle"""
        for key, value in self.languages.items():
            print(key, value)

    def writeSRTFile(self, folder, filename):
        tree = ET.parse(self.subtitle)
        root = tree.getroot()
        with open(os.path.join(folder, filename + ".tsv"), 'w') as f:
            f.write('Start\tEnd\tSubtitle\n')
            for child in root:
                if "start" in child.attrib and "dur" in child.attrib and child.text:
                    f.write(self.printSRTLine(child.attrib["start"], child.attrib["dur"], child.text))

    def formatSRTTime(self, secTime):
        """Convert a time in seconds (in Google's subtitle) to SRT time format"""
        sec, micro = str(secTime).split('.')
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        return "{:02}:{:02}:{:02}.{}".format(h,m,s,micro)

    def printSRTLine(self, start, duration, text):
        """Print a subtitle in SRT format"""
        end = self.formatSRTTime(float(start) + float(duration))
        start = self.formatSRTTime(float(start))
        text = self.convertHTML(text)
        return "{}\t{}\t{}\n".format(start, end, text)

    def convertHTML(self, text):
        """A few HTML encodings replacements.
            &#39; to '
        """
        return text.replace('&#39;', "'").replace('\n','').replace('\t','')
