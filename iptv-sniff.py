from sniff.web_live import web_live
from sniff.utils.m3u import m3u
from sniff.utils.tv import tv

import importlib
import argparse
import logging
import json
import sys
import os


def load_module(string):

    module = importlib.import_module("sniff.plugins.%s"%(string))
    return getattr(module, string)

def iptv_sniff(config, path, logger):

    tv_obj = tv.load(config, logger)

    playlist = os.path.join(path, tv_obj.m3ulist)

    m3ulist = m3u.load(playlist, logger)

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
                m3u8file = os.path.join(path, info["m3u8"])

                try:
                    live_plugin = load_module(info["plugin"])
                except (AttributeError, ModuleNotFoundError) as err:
                    logger.error("%s - plugin %s not supported!"%(err, info["plugin"]))
                    continue

                live = live_plugin(channel, [website, liveapi, headers], extinfo, referer, logger)

                print("checking %s"%(m3u8file))
                is_alive = live.check_alive(m3u8file)
                if is_alive:
                    print("%s is alive"%(info["m3u8"]))
                    continue

                try:
                    channel = live.sniff_stream()
                except Exception:
                    logger.error("plugin %s catch exception!"%(info["plugin"]), exc_info=True)
                    continue
                if channel is not None:
                    m3ulist.update_channel(channel)

                live.sniff_m3u8_file(m3u8file)

    m3ulist.dump_m3u(playlist)
    m3ulist.dump_txt(os.path.join(path, tv_obj.txtlist))

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
            default="tv.json",
            required=False,
            help="web sniff configure file"
            )
    parser.add_argument(
            "-o",
            "--output",
            action="store",
            default="playlist",
            required=False,
            help="m3u or txt playlist/m3u8 files store path"
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

    iptv_sniff(args.config, args.output, logger)
