from urllib.parse import urljoin
import requests
import logging
import m3u8
import os

def is_url(uri):
    return uri.startswith(('https://', 'http://'))

def base_uri(url):
    return '/'.join(url.split('/')[:-1]) + '/'


EXTINFO_FORMAT = '#EXTINF:-1 tvg-id="%s" tvg-name="%s" tvg-logo="%s" group-title="%s",%s'

class web_live:

    def __init__(self, chname, request_info, extinfo, referer, logger):

        self.chname  = chname
        self.website = request_info[0]
        self.liveapi = request_info[1]
        self.headers = request_info[2]
        self.extinfo = extinfo
        self.referer = referer
        self.logger  = logger

        self.link = ""

    def dump_link(self):

        return self.link

    def check_alive(self, uri):

        is_alive = False
        if is_url(uri):
            try:
                response = requests.get(uri, headers=self.headers)
                response.raise_for_status()
                if response.status_code == 200:
                    is_alive = True
            except requests.exceptions.RequestException as err:
                self.logger.error(err)
        else:
            if os.path.exists(uri):
                obj_m3u8 = m3u8.load(uri)
                for playlist in obj_m3u8.playlists:
                    is_alive = self.check_alive(playlist.uri)
                    return is_alive
        return is_alive

    def dump_custom_m3u8(self, link, m3u8file):

        os.makedirs(os.path.dirname(m3u8file), exist_ok=True)
        with open(m3u8file, 'w') as fd:
            fd.write("#EXTM3U\n") 
            fd.write("#EXT-X-VERSION:3\n")
            fd.write("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2560000\n") 
            fd.write(link)

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
            for media in playlist.media:
                if not is_url(media.uri):
                    media.uri = urljoin(base_path, media.uri)
        obj_m3u8.dump(m3u8file)
