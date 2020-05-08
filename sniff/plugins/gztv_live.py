from sniff.web_live import web_live
from urllib.parse import urlencode

import subprocess
import requests
import json
import time
import re
import os


class gztv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))

        data = {'id': self.chname,
                'commentFrontUrl': 'https://comment.gztv.com/commentf'}
        params = urlencode(data)
        liveurl = "%s?%s"%(self.liveapi, params)
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        find = re.findall(r"standardUrl=\'(https?.*m3u8.*)\'", response.text)
        if find:
            link = find[0].replace('\\','')
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        else:
            self.logger.error("m3u8 link not found!")
            return None

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
