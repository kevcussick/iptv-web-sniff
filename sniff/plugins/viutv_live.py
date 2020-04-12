from sniff.web_live import web_live

import subprocess
import requests
import random
import json
import time
import re
import os


class viutv_live(web_live):

    def __init__(self, chname, request_info, extinfo, referer, logger):

        web_live.__init__(self, chname, request_info, extinfo, referer, logger)

    def sniff_stream(self):

        print("probe website %s ......"%(self.website))
        liveurl = self.liveapi
        device_id = "".join(random.choice("abcdef0123456789") for _ in range(18))
        data = {'callerReferenceNo': time.strftime('%Y%m%d%H%M%S'),
                'channelno': '0'+self.chname,
                'mode': 'prod',
                'deviceId':device_id,
                'deviceType':'5',
                'format':'HLS'}
        try:
            response = requests.post(liveurl, json=data, headers=self.headers)
            response.encoding = 'utf-8'
            json_data = response.text
        except:
            curl_cmd = ['curl', '-s', '--cipher', 'AES256-SHA256', \
                       '-A', self.headers["User-Agent"], '--referer', self.headers["Referer"], \
                       '-d', json.dumps(data), '-H', 'Content-Type: application/json', liveurl]
            try:
                process = subprocess.run(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                json_data = process.stdout
            except subprocess.CalledProcessError as err:
                self.logger.error(err.output)
                return None
        try:
            info = json.loads(json_data)
            if info['responseCode'] == "SUCCESS":
                link = info['asset']['hls']['adaptive'][0]
                if link:
                    print("  {0: <20}{1:}".format(self.extinfo[4], link))
                    channel = self.extinfo + [link] + [self.headers["Referer"] if self.referer == 1 else ""]
                    self.link = link
                    return channel
                else:
                    self.logger.error(info)
                    return None
            else:
                self.logger.error(info["responseCode"])
                return None
        except ValueError:
            self.logger.error(json_data)
            return None
