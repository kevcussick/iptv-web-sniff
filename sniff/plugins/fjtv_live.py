from sniff.web_live import web_live

import subprocess
import requests
import hashlib
import json
import time
import re
import os


class fjtv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = "%s?id=%s"%(self.liveapi, self.chname)
        epoch = int(time.time())
        str = "97143b56f8c6b165201dfbabebc11592&YTE3Nzc0NmE5ODYzNWNiYWY2ODAwNmViNzk1M2VmZDM=&1.0.0&%s"%(epoch)
        hl = hashlib.md5()
        hl.update(str.encode(encoding="utf-8"))
        headers = {
            "X-API-TIMESTAMP": "%s"%(epoch),
	    "X-API-KEY": "97143b56f8c6b165201dfbabebc11592",
	    "X-AUTH-TYPE": "md5",
	    "X-API-VERSION": "1.0.0",
	    "X-API-SIGNATURE": hl.hexdigest(),
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"
        }
        try:
            response = requests.get(liveurl, headers=headers, timeout=(1, 5))
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            link = info[0]['channel_stream'][0]['url']
            link = link.replace(r'stream1','nclive')
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None
