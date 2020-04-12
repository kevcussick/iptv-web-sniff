from sniff.web_live import web_live
from sniff.utils.m3u import m3u

import importlib
import argparse
import logging
import json
import sys
import os


def load_module(string):
    module = importlib.import_module("sniff.plugins.%s"%(string))
    return getattr(module, string)


def web_sniff(tvdb, path, logger):

    if tvdb is None: tvdb = "./tvdb.txt"
    if path is None: path = "./playlist"

    playlist = os.path.join(path, "webtv.m3u")

    m3ulist = m3u.load(playlist, logger)

    with open(tvdb) as file_obj:

        info = json.load(file_obj)
        for index in info:
            active = info[index]["active"]
            if active == 0:
                continue
            channel = info[index]["channel"]
            website = info[index]["website"]
            liveapi = info[index]["liveapi"]
            headers = info[index]["headers"]
            referer = info[index]["referer"]
            extinfo = [
                        info[index]["m3uinfo"]["tvg-id"],
                        info[index]["m3uinfo"]["tvg-name"],
                        info[index]["m3uinfo"]["tvg-logo"],
                        info[index]["m3uinfo"]["group-title"],
                        info[index]["m3uinfo"]["title"]
                      ]
            m3u8file = os.path.join(path, info[index]["m3u8"])

            try:
                live_plugin = load_module(info[index]["plugin"])
            except AttributeError:
                logger.error("plugin %s not supported!"%(info[index]["plugin"]))
                continue

            live = live_plugin(channel, [website, liveapi, headers], extinfo, referer, logger)

            print("checking %s"%(m3u8file))
            is_alive = live.check_alive(m3u8file)
            if is_alive:
                print("%s is alive"%(info[index]["m3u8"]))
                continue

            channel = live.sniff_stream()
            if channel is not None:
                m3ulist.update_channel(channel)

            live.sniff_m3u8_file(m3u8file)

        m3ulist.dump_m3u(playlist)

if __name__ == '__main__':

    parser=argparse.ArgumentParser(
            description='web stream sniff tool'
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
    parser.add_argument(
            "-o",
            "--output",
            action="store",
            required=False,
            help="m3u playlist/m3u8 file store path"
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
    logger = logging.getLogger("web sniff")

    web_sniff(args.config, args.output, logger)
