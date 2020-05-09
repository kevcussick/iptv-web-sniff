from sniff.web_live import web_live

from urllib.parse import urlparse, urlunparse
import requests
import json
import time
import re
import os


class ifeng_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))

        epoch = "%x"%int(time.time()+1800)
        input = "obb9Lxyv5C"+self.chname+epoch
        link = self.liveapi%(self.chname, self.md5(input), epoch)
        print("  {0: <20}{1:}".format(self.extinfo[4], link))
        channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
        self.link = link
        return channel

    def sniff_m3u8_file(self, m3u8file):

        self.dump_custom_m3u8(self.link, m3u8file)
