from sniff.web_live import web_live

from urllib.parse import urlencode, urlparse
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from base64 import b64decode

import subprocess
import requests
import json
import time
import re
import os


class sttv_live(web_live):

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
        info = json.loads(response.text)
        try:
            info = json.loads(response.text)
            if info["status"] != "ok":
                self.logger.error(info)
                return None

            for channel in info["data"]["tv"]:
                if channel["ChannelId"] == self.chname:
                    link = channel["liveurl"]
                    break
            if not link:
                self.logger.error("m3u8 link not found!")
                self.logger.error(info)
                return None
        except (ValueError, KeyError) as err:
            self.logger.error("%s - %s"%(err, response.text))

        liveurl = "https://sttv2-api.cutv.com/api/getIP.php"
        try:
            response = requests.get(liveurl, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        info = json.loads(response.text)
        try:
            info = json.loads(response.text)
            if info["status"] != "ok":
                self.logger.error(info)
                return None
            ciphertext = b64decode(info["data"][0])

        except (ValueError, KeyError) as err:
            self.logger.error("%s - %s"%(err, response.text))
            return None

        epoch = "%x"%(int(time.time()) + 7200)
        key = bytearray('reter4446fdfgdfg', 'utf-8')
        iv  = bytearray('0102030405060708', 'utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        url = urlparse(link)
        salt = 'j5dt4yng0nux7s8bew1r1gip'
        sign = self.md5(plaintext.decode('utf-8') + salt + url.path + epoch)

        link = "%s?sign=%s&t=%s"%(link, sign, epoch)
        print("  {0: <20}{1:}".format(self.extinfo[4], link))
        channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
        self.link = link
        return channel
