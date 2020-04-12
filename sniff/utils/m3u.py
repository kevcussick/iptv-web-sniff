#!/usr/bin/python3

import urllib.request
import random
import re
import os


def is_url(uri):
    return uri.startswith(('https://', 'http://'))

def is_extinfo(info):
    return info.startswith("#EXTINF:")

def is_streamlink(uri):
    return uri.startswith(('https://', 'http://', 'rtp://', 'rtmp://', 'rtsp://'))

def string_to_lines(string):
    return string.strip().splitlines()


EXTINFO_FORMAT = '#EXTINF:-1 tvg-id="%s" tvg-name="%s" tvg-logo="%s" group-title="%s",%s'

class m3u:

    def __init__(self, content, logger):

        self.logger = logger
        self.database = []
        if content:
            self.__parse_m3u(content)

    @staticmethod
    def load(uri, logger):
    
        content = ""
        if is_url(uri):
            try:
                response = requests.get(uri)
                response.raise_for_status()
                response.encoding = 'utf-8'
                content = response.text
            except requests.exceptions.HTTPError as err:
                print(err.response.text)
        else:
            if os.path.exists(uri):
                with open(uri, "r") as fileobj:
                    content = fileobj.read().strip()
    
        return m3u(content, logger)
    
    @staticmethod
    def loads(content, logger):
    
        return m3u(content, logger)

    def __parse_m3u(self, content):

        extinfo_found  = False
        for line in string_to_lines(content):
            if is_extinfo(line):
                channel_info = self.__parse_info(line)
                extinfo_found = True

            elif is_streamlink(line):
                if not extinfo_found:
                    continue
                extinfo_found = False
                channel_info.append(line)
                self.logger.info(channel_info)

                channel = {}
                channel["id"]    = channel_info[0]
                channel["name"]  = channel_info[1]
                channel["logo"]  = channel_info[2]
                channel["group"] = channel_info[3]
                channel["title"] = channel_info[4]
                channel["link"]  = channel_info[5]
                self.database.append(channel)

    def __parse_info(self, info):

        [tvg_id, tvg_name, tvg_logo, tvg_group, tvg_title] = ["", "", "", "", ""]
        m = re.search("tvg-id=\"(.*?)\"", info)
        if m: tvg_id = m.group(1)
        m = re.search("tvg-name=\"(.*?)\"", info)
        if m: tvg_name = m.group(1)
        m = re.search("tvg-logo=\"(.*?)\"", info)
        if m: tvg_logo = m.group(1)
        m = re.search("group-title=\"(.*?)\"", info)
        if m: tvg_group = m.group(1)
        m = re.search("[,](?!.*[,])(.*?)$", info)
        if m: tvg_title = m.group(1)
        return [tvg_id, tvg_name, tvg_logo, tvg_group, tvg_title]

    def __query_channel(self, title):

        for channel in self.database:
            if channel["title"] == title:
                return channel
        return None

    def query_link(self, title):

        for channel in self.database:
            if channel["title"] == title:
                return channel["link"]
        return ""

    def update_channel(self, channel):

        tvg_id, tvg_name, tvg_logo, group_title, title, link, referer = channel

        new_channel = self.__query_channel(title)
        if new_channel is None:
            new_channel = {}
            new_channel["id"]    = tvg_id
            new_channel["name"]  = tvg_name
            new_channel["logo"]  = tvg_logo
            new_channel["group"] = group_title
            new_channel["title"] = title
            if not referer:
                new_channel["link"] = link
            else:
                new_channel["link"] = link + "|Referer=" + referer

            self.database.append(new_channel)
        else:
            new_channel["id"]    = tvg_id
            new_channel["name"]  = tvg_name
            new_channel["logo"]  = tvg_logo
            new_channel["group"] = group_title
            new_channel["title"] = title
            if not referer:
                new_channel["link"] = link
            else:
                new_channel["link"] = link + "|Referer=" + referer
        
    def dumps(self):

        content = "#EXTM3U\n"
        for channel in self.database:
            channel_info = EXTINFO_FORMAT%(channel["id"], channel["name"], channel["logo"], channel["group"], channel["title"])
            content += channel_info + "\n" + channel["link"] + "\n"
        return content

    def dump_m3u(self, filepath):

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        m3u_header = "#EXTM3U\n"
        with open(filepath, 'w') as fileobj:
            fileobj.write(m3u_header)
            for channel in self.database:
                channel_info = EXTINFO_FORMAT%(channel["id"], channel["name"], channel["logo"], channel["group"], channel["title"])
                fileobj.write(channel_info + "\n" + channel["link"] + "\n")
  
    def dump_txt(self, filepath):

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as fileobj:
            for channel in self.database:
                fileobj.write(channel["title"] + "," + channel["link"] + "\n")

    def dump_json(self):
        #TODO
        print("Not implemented")
