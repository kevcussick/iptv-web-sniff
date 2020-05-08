from sniff.web_live import web_live, is_url

import subprocess
import requests
import m3u8
import json
import time
import re
import os


class cibn_live(web_live):


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
        info = json.loads(response.text)
        try:
            info = json.loads(response.text)
            if info["code"] != "1000":
                self.logger.error(info)
                return None
            for channel in info["data"]["channelList"]:
                if channel["channelId"] == int(self.chname):
                    link = channel["m3u8"]
                    print("  {0: <20}{1:}".format(self.extinfo[4], link))
                    channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
                    self.link = link
                    return channel
            self.logger.error(info)
            return None
        except ValueError:
            self.logger.error(response.text)
            return None

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
