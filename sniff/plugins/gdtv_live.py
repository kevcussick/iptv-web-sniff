from sniff.web_live import web_live

import subprocess
import requests
import hashlib
import json
import time
import re
import os


class gdtv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = "%s?id=%s"%(self.liveapi, self.chname)
        epoch = int(time.time())
        str = "55f703e33e613e9482e1181ca8c71751&Njc4YWVlMTA5YTg1NmRiYzQxZDBlNjhiNGRkMDQ0NWM=&1.0.0&%s"%(epoch)
        hl = hashlib.md5(str.encode(encoding="utf-8"))
        headers = {

            "X-API-TIMESTAMP": "%s"%(epoch),
	    "X-API-KEY": "55f703e33e613e9482e1181ca8c71751",
	    "X-AUTH-TYPE": "md5",
	    "X-API-VERSION": "1.0.0",
	    "X-API-SIGNATURE": hl.hexdigest(),
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0"
        }
        try:
            response = requests.get(liveurl, headers=self.headers)
            #response = requests.get(liveurl, headers=headers)
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
