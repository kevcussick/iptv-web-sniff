# iptv-web-sniff
A web stream sniff and proxy tool

## dependencies
This tool only support python3 and requires m3u8 package.
```console
$ pip3 install -U m3u8
```

## usage

### sniff web stream
```console
$ python3 iptv-sniff.py -c config.json -o playlist/
```
This will sniff all the APIs listed in tvdb and dump a m3u playlist named tv.m3u,
then please use iptv player to add webtv.m3u when finished.

And enjoy it!

### iptv proxy server
```console
$ python3 iptv-proxy.py -c config.json &
```
- **make your own m3u playlist with proxy stream:**

	1. modify the ip address and port in config.json

	2. generate the m3u playlist of your own server
```console
	$ python3 iptv-list.py -c config.json &
```


- **play single stream example:**

	ffplay http://192.168.1.1:8080/channel?cnn.m3u8
