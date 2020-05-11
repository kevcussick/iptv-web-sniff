from sniff.web_live import web_live

from urllib.parse import urlencode
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

import subprocess
import requests
import json
import time
import re
import os


class fourgtv_live(web_live):

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
        except (ValueError, KeyError) as err:
            self.logger.error("%s - %s"%(err,response.text))
            return None

        key = b'ilyB29ZdruuQjC45JhBBR7o2Z8WJ26Vg'
        iv  = b'JUMxvVMmszqUTeKn'
        raw = {"fnCHANNEL_ID":info["Data"]["fnID"],"fsASSET_ID":info["Data"]["fs4GTV_ID"],"fsDEVICE_TYPE":"pc","clsIDENTITY_VALIDATE_ARUS":{"fsVALUE":""}}
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = bytes(json.dumps(raw), 'utf-8')
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        value = b64encode(ciphertext).decode('utf-8')
        data = {'value': value}
        liveurl = "https://api2.4gtv.tv/Channel/GetChannelUrl3"
        try:
            response = requests.post(liveurl, data=data, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            return None
        response.encoding = 'utf-8'
        try:
            info = json.loads(response.text)
            if not info["Success"]:
                self.logger.error(info)
                return None
            ciphertext = b64decode(info["Data"])
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
            info = json.loads(plaintext.decode('utf-8'))
            link = info["flstURLs"][1]
            print("  {0: <20}{1:}".format(self.extinfo[4], link))
            channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
            self.link = link
            return channel
        except (ValueError, KeyError) as err:
            self.logger.error("%s - %s"%(err,response.text))
            return None
