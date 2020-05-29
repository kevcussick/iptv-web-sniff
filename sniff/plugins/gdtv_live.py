from sniff.web_live import web_live

from urllib.parse import urlencode
from Crypto.Cipher import AES
from base64 import b64decode

import subprocess
import requests
import json
import time
import re
import os


class gdtv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def __drm_player(self):

        epoch = "%d"%int(time.time()*1000)
        key = bytearray.fromhex("f056180ec970b169980f108c13305642")
        iv  = bytearray.fromhex("912467427aa54cccf443d2ae206a63ce")
        ciphertext = b64decode("vNIR0lurDuCNBzpTozmlU9kxA/SEwuReipfVHWhbEW8=")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        salt = unpad(cipher.decrypt(ciphertext), AES.block_size)
        url = "http://stream1.grtn.cn/%s/sd/live.m3u8"%self.chname
        refererurl = "http://www.gdtv.cn/tv/"
        playerVersion = "4.12.180327_RC"
        string = playerVersion + refererurl + epoch + url
        hash_s = self.md5(salt.decode('utf-8') + string + salt.decode('utf-8'))

        headers = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"}
        data = {'url': url,
                'refererurl': refererurl,
                'hash': hash_s,
                'time': epoch,
                'playerVersion': playerVersion}
        params = urlencode(data)
        liveurl = "http://live.grtn.cn/drm.php?%s"%params
        try:
            response = requests.get(liveurl, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        link = response.text
        return link

    def __m2o_player(self):

        liveurl = "%s?id=%s"%(self.liveapi, self.chname)
        epoch = int(time.time()*1000)
        string = "55f703e33e613e9482e1181ca8c71751&Njc4YWVlMTA5YTg1NmRiYzQxZDBlNjhiNGRkMDQ0NWM=&1.0.0&%s"%(epoch)
        signature = self.md5(string)
        headers = {
            "X-API-TIMESTAMP": "%d"%(epoch),
            "X-API-KEY": "55f703e33e613e9482e1181ca8c71751",
            "X-AUTH-TYPE": "md5",
            "X-API-VERSION": "1.0.0",
            "X-API-SIGNATURE": signature,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"}
        try:
            response = requests.get(liveurl, headers=self.headers)
            #response = requests.get(liveurl, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            link = info[0]['channel_stream'][0]['url']
            link = link.replace('stream1','nclive')
            return link
        except (ValueError, KeyError):
            self.logger.error(response.text)
            return None

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        link = self.__m2o_player()
        if link:
            link = link.replace('stream1','nclive')
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        else:
            self.logger.error("m3u8 link not found!")
            return None
