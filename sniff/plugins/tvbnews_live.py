from sniff.web_live import web_live

import requests
import re
import os


class tvbnews_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

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
        find = re.findall(r'vjvars.vdo_url\s=\s"(https?.*m3u8.*)"', response.text)
        if find:
            link = find[0].replace('\\','')
            try:
                response = requests.get(link, headers=self.headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                self.logger.error(err)
                return None

            if response.history:
                self.logger.warning("%s %s"%(response.status_code, response.url))

            link = response.url
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        else:
            self.logger.error("m3u8 link not found!")
            return None
