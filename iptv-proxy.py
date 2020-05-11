from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from urllib import parse

from sniff.web_live import web_live
from sniff.utils.m3u import m3u
from sniff.utils.tv import tv

import importlib
import argparse
import logging
import json
import sys
import os


tv_table = {}

def load_module(string):

    module = importlib.import_module("sniff.plugins.%s"%(string))
    return getattr(module, string)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):

        pass

def iptv_proxy_handler(tvdb, logger):

    class custom_iptv_proxy_handler(BaseHTTPRequestHandler):

        def do_GET(self):
            #http://192.168.1.1:8080/channel?cnn.m3u8
            parsed_path = parse.urlparse(self.path)

            reply_done = False
            m3u8 = parsed_path.query
            try:
                live = tv_table[m3u8]

                link = live.dump_link()
                if link:
                    self.send_response(301)
                    self.send_header('Location', link)
                    self.end_headers()

                    reply_done = True

                    if live.check_alive(link):
                        print("%s is alive!"%(m3u8))
                        return

                try:
                    channel = live.sniff_stream()
                except Exception:
                    logger.error("plugin catch exception!", exc_info=True)

                if channel is not None:
                    link = live.dump_link()
                    self.send_response(301)
                    self.send_header('Location', link)
                    self.end_headers()

                    reply_done = True
            except (ValueError, KeyError):
                logger.error("channel %s not supported!"%m3u8)

            if not reply_done: self.send_error(404)

    return custom_iptv_proxy_handler

def iptv_proxy(config, logger):

    tv_obj = tv.load(config, logger)

    print(tv_obj.source)
    for source in tv_obj.source:
        if not os.path.exists(source):
            logger.error("%s is not existed!"%(source))
            continue

        with open(source) as file_obj:

            tvlive = json.load(file_obj)
            for info in tvlive:
                active = info["active"]
                if active == 0:
                    continue
                channel = info["channel"]
                website = info["website"]
                liveapi = info["liveapi"]
                headers = info["headers"]
                referer = info["referer"]
                extinfo = [
                            info["m3uinfo"]["tvg-id"],
                            info["m3uinfo"]["tvg-name"],
                            info["m3uinfo"]["tvg-logo"],
                            info["m3uinfo"]["group-title"],
                            info["m3uinfo"]["title"]
                          ]

                try:
                    live_plugin = load_module(info["plugin"])
                except (AttributeError, ModuleNotFoundError) as err:
                    logger.error("%s - plugin %s not supported!"%(err, info["plugin"]))
                    continue

                live = live_plugin(channel, [website, liveapi, headers], extinfo, referer, logger)

                m3u8 = info["m3u8"]
                tv_table[m3u8] = live

    try:
        httpd = ThreadingHTTPServer(('0.0.0.0', int(tv_obj.server["port"])), iptv_proxy_handler(tv_table, logger))
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':

    parser=argparse.ArgumentParser(
            description='web tv proxy tool'
            )
    parser.add_argument(
            "-v",
            "--verbosity",
            action="count",
            default=0,
            help="increase output verbosity"
            )
    parser.add_argument(
            "-c",
            "--config",
            action="store",
            default="tv.json",
            required=False,
            help="web sniff configure file"
            )

    args = parser.parse_args()

    log_level = args.verbosity
    if log_level == 0:
        logging_level = logging.WARN
    if log_level == 1:
        logging_level = logging.INFO
    if log_level >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s: %(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S",
                        level=logging_level
                        )
    logger = logging.getLogger("iptv proxy")

    iptv_proxy(args.config, logger)
