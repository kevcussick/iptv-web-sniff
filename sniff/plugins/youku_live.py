from sniff.web_live import web_live, is_url

import subprocess
import requests
import hashlib
import random
import m3u8
import json
import time
import re
import os


class youku_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        liveId = self.chname

        try:
            tt = str(int(time.time()*1000))
            data = json.dumps({"liveId":liveId,"app":"Pc"}, separators=(',', ':'))
            url = 'https://acs.youku.com/h5/mtop.youku.live.com.livefullinfo/1.0/?appKey=24679788'
            with requests.Session() as s:
                cookies = s.get(url, headers=self.headers, timeout=(1, 2)).cookies
                token = requests.utils.dict_from_cookiejar(cookies).get('_m_h5_tk')[0:32]
                sign = hashlib.md5((token + '&' + tt + '&' + '24679788' + '&' + data).encode('utf-8')).hexdigest()
                params = {
                    't': tt,
                    'sign': sign,
                    'data': data
                }
                response = s.get(url, params=params).json()
                name = response.get('data').get('data').get('name')
                streamName = response.get('data').get('data').get('stream')[0].get('streamName')
                link = 'http://lvo-live.youku.com/vod2live/{}_mp4hd2v3.m3u8?&expire=21600&psid=1&ups_ts={}&vkey='.format(streamName, int(time.time()))
                print("  {0: <20}{1:}".format(self.extinfo[4], link))
                channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
                self.link = link
                return channel
        except:
            self.logger.error("auth failed!")
            return None

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
