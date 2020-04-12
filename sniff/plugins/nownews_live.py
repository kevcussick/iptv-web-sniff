from sniff.web_live import web_live

import requests
import time
import json
import re
import os


class nownews_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        request_info[1] = request_info[1]%(time.strftime("%Y%m%d%H%M%S"))
        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            if info['responseCode'] == "SUCCESS":
                link = info['asset']['hls']['adaptive'][0]
                if link:
                    print("  {0: <20}{1:}".format(self.extinfo[4], link))
                    channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
                    self.link = link
                    return channel
                else:
                    self.logger.error(info)
                    return None
            else:
                self.logger.error(info["responseCode"])
                return None
        except ValueError:
            self.logger.error(response.text)
            return None
