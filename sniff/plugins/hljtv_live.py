from sniff.web_live import web_live

import subprocess
import requests
import json
import time
import re
import os


class hljtv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi%(self.chname)
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            link = info[0]['m3u8']
            self.extinfo[1] = info[0]['title']
            self.extinfo[4] = info[0]['title']
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
