# iptv-web-sniff
A web stream sniff and proxy tool

## usage

### sniff web stream
```console
$ python3 iptv-web-sniff.py -c tvdb.txt -o playlist/
```
This will sniff all the apis list in tvdb.txt and dump a m3u playlist name webtc.m3u,
then use iptv player to add the m3u playlist when finished and enjoy it!

### iptv proxy server
```console
$ python3 iptv-proxy.py -c tvdb.txt&
```
make your own m3u playlist with proxy stream:

Example:
http://192.168.1.1/channel?cnn.m3u8
