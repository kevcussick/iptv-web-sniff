from sniff.web_live import web_live, is_url

import subprocess
import requests
import m3u8
import json
import time
import re
import os


class mtxjtv_live(web_live):


    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        data = {
                'cdnEncrypt':'d058c6c09b8cec3e4c8391557ac977714a35da41c4cfd40c75d6b4fdb37750b43af74fce34817cf0f28fdb861cee29c2d38a224f664092fc607624d364573a5bf191b7df418a898adfe4f7daed74bd464c636814747c2b246677746a3cda962610392572de95ce9db9447ce86a2f5f6df3ae1405b07d8a0b94e218d92ddc61345eb64ad9db24c0b38f20d17c3717682f41fad9b9f86009a3ecd06a4f448d26362cbd0ecd8e3358f60737b11e812b54afdfcc0ac3d66b87caaf0ee33751a81e585973a2f1b0591d39901f7b12ace04fa9de8c971789df6d33e7877c434a7c6b7cdd61ed26eb0bcefa7bb153d50e3912e5d3d0be3c09e3a44d7d87889d78ec782db6f78cffd8abde3550278369be903885039b250473e0c7679bcdd7a90adc84d78ae10719513c792fd5d85147d606ba6e534edd342d0279431bd9668e0982b6ea',
                'cdnIndex':0,
                'playType':'live',
                'type':'cdn',
                'url':'http://livehyw.chinamcache.com/xjtvs/zb000%s.m3u8'%(self.chname)}

        try:
            response = requests.post(liveurl, json=data, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'

        try:
            info = json.loads(response.text)
            if info["code"] != "0000":
                self.logger.error(info)
                return None
            link = info["url"]
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None
