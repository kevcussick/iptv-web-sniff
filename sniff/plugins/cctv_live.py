from sniff.web_live import web_live, is_url
from urllib.parse import urlencode

import subprocess
import requests
import hashlib
import random
import m3u8
import json
import time
import re
import os


class cctv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))

        vdn_tsp = str(int(time.time()))
        vdn_vn = "2054"
        staticCheck = "F9F4F4E4FC4ED0BEEB39165E950344A2"
        vdn_uid = ""
        vdn_pcv = "152438790"
        vdn_vc = self.md5(vdn_tsp + vdn_vn + staticCheck + vdn_uid).upper()
        params = {
            'tai': 'ipad',
            'from': 'html5',
            'pid': self.chname,
            'tsp': vdn_tsp,
            'vn': vdn_vn,
            'vc': vdn_vc,
            'pcv': vdn_pcv,
            'uid': vdn_uid
        }
        liveurl = "%s?%s"%(self.liveapi, urlencode(params))
        print(liveurl)
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        find = re.findall(r"var\shtml5VideoData\s=\s'({.*})", response.text)
        if find:
            try:
                info = json.loads(find[0])
                if info["status"] != "001":
                    self.logger.error(info)
                    return None
                link = info["hls_url"]
                print("  {0: <20}{1:}".format(self.extinfo[4], link))
                channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
                self.link = link
                return channel
            except ValueError:
                self.logger.error(response.text)
                return None
        else:
            self.logger.error("m3u8 link not found!")
            return None
