from sniff.web_live import web_live

import requests
import re
import os


class freeintertv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        data = {'chname': self.chname,
                'ch': "http://www.freeintertv.com/externals/tv-russia/smotret-tv3-online",
                'html5': '11'}
        try:
            response = requests.post(liveurl, data=data, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        find = re.findall(r"(http?s.*m3u8)", response.text)
        if find:
            link = find[0].replace('\\','')
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        else:
            self.logger.error("m3u8 link not found!")
            return None
