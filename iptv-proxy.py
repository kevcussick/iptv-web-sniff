from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib import parse

from sniff.web_live import web_live
from sniff.utils.m3u import m3u

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


class iptv_proxy_handler(BaseHTTPRequestHandler):

    def do_GET(self):
        #http://192.168.1.1:8080/channel?cnn.m3u8
        parsed_path = parse.urlparse(self.path)

        try:
            m3u8 = parsed_path.query
            live = tv_table[m3u8]

            link = live.dump_link()
            if link:
                self.send_response(301)
                self.send_header('Location', link)
                self.end_headers()
                if live.check_alive(link):
                    print("%s is alive!"%(m3u8))
                    return

            channel = live.sniff_stream()
            if channel is not None:
                link = channel[5]
                self.send_response(301)
                self.send_header('Location', link)
                self.end_headers()
            else:
                self.send_error(404)
        except:
            self.send_error(404)


def iptv_proxy(tvdb, logger):

    if not tvdb: tvdb = "./tvdb.txt"
    if not os.path.exists(tvdb):
        logger.error("tvdb.txt is not existed!")
        return

    with open(tvdb) as file_obj:

        tvlives = json.load(file_obj)
        for tv in tvlives:
            active = tv["active"]
            if active == 0:
                continue
            channel = tv["channel"]
            website = tv["website"]
            liveapi = tv["liveapi"]
            headers = tv["headers"]
            referer = tv["referer"]
            extinfo = [
                        tv["m3uinfo"]["tvg-id"],
                        tv["m3uinfo"]["tvg-name"],
                        tv["m3uinfo"]["tvg-logo"],
                        tv["m3uinfo"]["group-title"],
                        tv["m3uinfo"]["title"]
                      ]

            try:
                live_plugin = load_module(tv["plugin"])
            except AttributeError:
                logger.error("plugin %s not supported!"%(tv["plugin"]))
                continue

            live = live_plugin(channel, [website, liveapi, headers], extinfo, referer, logger)

            m3u8 = tv["m3u8"]
            tv_table[m3u8] = live

    try:
        server = HTTPServer(('0.0.0.0', 8080), iptv_proxy_handler)
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':

    parser=argparse.ArgumentParser(
            description='web m3u8 sniff tool'
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
            required=False,
            help="web sniff channel database"
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
