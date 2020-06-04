from sniff.web_live import web_live

import urllib.parse
import ipaddress
import requests
import random
import json
import re
import os


class tvbnews_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))

        ip_pool = [str(ip) for ip in ipaddress.IPv4Network('112.118.0.0/16')]

        ip = random.choice(ip_pool)
        token = "http://token.tvb.com/stream/live/hls/mobilehd_%s.smil?app=news&feed&client_ip=%s"%(self.chname, ip)

        liveurl = "%s?token=%s"%(self.liveapi, urllib.parse.quote(token, safe=''))
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'

        try:
            info = json.loads(response.text)
            link = info["url"]
        except ValueError:
            self.logger.error(response.text)
            return None

        try:
            response = requests.get(link, headers=self.headers, allow_redirects=False)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None

        if response.status_code != 302:
            self.logger.error("m3u8 link not found!")
            return None

        link = response.headers["Location"]
        print("  {0: <20}{1:}".format(self.extinfo[4], link))
        channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
        self.link = link
        return channel

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
