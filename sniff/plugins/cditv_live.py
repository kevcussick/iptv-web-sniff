from sniff.web_live import web_live

import subprocess
import requests
import json
import time
import re
import os


class cditv_live(web_live):

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
            if not info['data']['ios_HDlive_url']:
                link = info['data']['ios_url']
            else:
                link = info['data']['ios_HDlive_url']
            self.extinfo[1] = info['data']['title']
            self.extinfo[2] = info['data']['thumb']
            self.extinfo[4] = info['data']['title']
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None
