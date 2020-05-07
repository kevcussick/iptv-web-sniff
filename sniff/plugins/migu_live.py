from sniff.web_live import web_live

from urllib.parse import urlparse, urlunparse
import requests
import json
import re
import os


class migu_live(web_live):

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
            if info["code"] != "200":
                self.logger.error(info)
                return None
            link = info["body"]["urlInfo"]["url"]
            link_orig = link
            link = link.replace('/1200/','/2500/')
            link = link.replace('/1500/','/3000/')
            link = link.replace('/51/','/57/')
            u = urlparse(link)
            result = u._replace(netloc='live.hcs.cmvideo.cn')
            link = urlunparse(result)
            if not self.check_alive(link):
                link = link_orig
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None
