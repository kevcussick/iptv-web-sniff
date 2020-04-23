from sniff.web_live import web_live, is_url

import subprocess
import requests
import m3u8
import json
import time
import re
import os


class jxntv_live(web_live):


    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def login_auth(self, epoch):

        if jxntv_live.login == True:
            return
        loginauth = "https://app.jxntv.cn/Qiniu/liveauth/authlogin.php?t=%d"%(epoch)
        try:
            response = requests.get(loginauth, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return
        jxntv_live.login = True

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi

        epoch = int(time.time())
        loginauth = "https://app.jxntv.cn/Qiniu/liveauth/authlogin.php?t=%d"%(epoch)
        try:
            response = requests.get(loginauth, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return

        getauth = "https://app.jxntv.cn/Qiniu/liveauth/getAuth.php?t=%d"%(epoch)
        try:
            response = requests.get(getauth, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        info = json.loads(response.text)
        try:
            print(response.text)
            info = json.loads(response.text)
            if info["up"] == 0:
                self.logger.error(info)
                return None
            token = info["token"]
            epoch = info["t"]
            link = liveurl%(self.chname, token, epoch)
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except ValueError:
            self.logger.error(response.text)
            return None
