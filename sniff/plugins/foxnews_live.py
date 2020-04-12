from sniff.web_live import web_live, is_url, base_uri
from urllib.parse import urljoin, urldefrag

import requests
import random
import json
import time
import m3u8
import re
import os


class foxnews_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            link = info["channel"]["item"]["media-group"]["media-content"][0]["@attributes"]["url"]
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None

    def sniff_m3u8_file(self, m3u8file):

        if self.link == "": return

        os.makedirs(os.path.dirname(m3u8file), exist_ok=True)
        try:
            response = requests.get(self.link, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return
        response.encoding = 'utf-8'
        obj_m3u8 = m3u8.loads(response.text)
        base_path = base_uri(self.link)
        for playlist in obj_m3u8.playlists:
            if not is_url(playlist.uri):
                playlist.uri = urljoin(base_path, playlist.uri)
            playlist.uri = urldefrag(playlist.uri)[0]
            for media in playlist.media:
                if not is_url(media.uri):
                    media.uri = urljoin(base_path, media.uri)
                meida.uri = urldefrag(playlist.uri)[0]
        obj_m3u8.dump(m3u8file)
