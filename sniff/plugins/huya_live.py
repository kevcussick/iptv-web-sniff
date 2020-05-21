from sniff.web_live import web_live, is_url

import subprocess
import requests
import random
import m3u8
import json
import time
import re
import os


class huya_live(web_live):

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
            return

        response.encoding = 'utf-8'
        find = re.findall(r'"stream": ({.+?})\s*};', response.text)
        if find:
            data = json.loads(find[0])
            #stream_info = random.choice(data['data'][0]['gameStreamInfoList'])
            stream_info = data['data'][0]['gameStreamInfoList'][0]
            sHlsUrl = stream_info['sHlsUrl']
            sStreamName = stream_info['sStreamName']
            sHlsUrlSuffix = stream_info['sHlsUrlSuffix']
            sHlsAntiCode = stream_info['sHlsAntiCode']
            hls_url = u'{}/{}.{}?{}'.format(sHlsUrl, sStreamName, sHlsUrlSuffix, sHlsAntiCode)
            link = self.unescape(hls_url)
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        else:
            self.logger.error(response.text)
            return None

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
