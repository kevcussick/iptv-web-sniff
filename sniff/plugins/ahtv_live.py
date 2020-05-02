from sniff.web_live import web_live

import subprocess
import requests
import json
import time
import re
import os


class ahtv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi

        try:
            data = {'catalog': "/pull.bdflv.ahtv.cn/live/%s"%(self.chname)}
            response = requests.post(liveurl, data=data, headers=self.headers)
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            sign = info["sign"]
            tick = info["time"]
            link = "http://pull.bdflv.ahtv.cn/live/%s.flv?timestamp=%s&secret=%s"%(self.chname, tick, sign)
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None
