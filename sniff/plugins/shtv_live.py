from sniff.web_live import web_live

import requests
import time
import re
import os


class shtv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        epoch = int(time.time()-300)
        if re.match(".*m3u8$", self.liveapi):
            link = self.liveapi
        else:
            link = "%s&ts=%d"%(self.liveapi, epoch)
        print("  {0: <20}{1:}".format(self.extinfo[4], link))
        channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
        self.link = link
        return channel
