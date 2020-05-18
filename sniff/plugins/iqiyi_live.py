from sniff.utils.iqiyi_util import get_random_str, get_macid, cmd5x_iqiyi3 as cmd5x
from sniff.web_live import web_live, is_url

from urllib.parse import urlencode
import subprocess
import requests
import m3u8
import json
import time
import re
import os


class iqiyi_live(web_live):


    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))

        tm = time.time()
        host = self.liveapi
        vid = self.chname
        params = {
            'lp': vid,
            'src': '01010031010000000000',
            'uid': '',
            'rateVers': 'PC_QIYI_3',
            'k_uid': get_macid(24),
            'qdx': 'n',
            'qdv': 3,
            'qd_v': 1,
            'dfp': get_random_str(66),
            'v': 1,
            'k_err_retries': 0,
            'tm': int(tm + 1),
        }
        src = '/live?{}'.format(urlencode(params))
        vf = cmd5x(src)
        st = int(tm * 1000)
        et = int((tm + 1296000) * 1000)
        c_dfp = '__dfp={}@{}@{}'.format(params['dfp'], et, st)

        liveurl = '{}{}&vf={}'.format(host, src, vf)
        self.headers['Cookie'] = c_dfp
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
            if info["code"] != "A00000":
                self.logger.error(info)
                return None
            for stream in info["data"]["streams"]:
                if stream["streamFormat"] == "TS" and stream["bitrate"] == "2128":
                    link = stream["url"]
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
