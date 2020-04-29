#!/usr/bin/python3

import urllib.request
import json
import os


class tv:

    def __init__(self, content, logger):

        self.logger = logger
        self.server = {}
        self.source = []
        self.m3ulist = "tv.m3u"
        self.txtlist = "tv.txt"
        if content:
            self.__parse_tv(content)

    @staticmethod
    def load(path, logger):
    
        content = ""
        if os.path.exists(path):
            with open(path, "r") as fileobj:
                content = fileobj.read().strip()
    
        return tv(content, logger)
    
    @staticmethod
    def loads(content, logger):
    
        return tv(content, logger)

    def __parse_tv(self, content):

        info = json.loads(content)
        try:
            info = json.loads(content)
        except ValueError:
            self.logger.error(content)
            return

        self.server["ip"]   = info["server"]["ip"]
        self.server["port"] = info["server"]["port"]

        self.m3ulist = info["m3ulist"]
        self.txtlist = info["txtlist"]

        for item in info["source"]:
            self.source.append(item)
