from sniff.web_live import web_live

import subprocess
import requests
import json
import time
import re
import os


class hkopentv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        epoch = int(time.time()*1000)

        try:
            response = requests.post(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        json_data = response.text
        try:
            info = json.loads(json_data)
            if info['rc'] == 0:
                link = info['rcode']
                if link:
                    print("  {0: <20}{1:}".format(self.extinfo[4], link))
                    channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
                    self.link = link
                    return channel
                else:
                    self.logger.error(info)
                    return None
            else:
                self.logger.error(info["rc"])
                return None
        except ValueError:
            self.logger.error(json_data)
            return None
