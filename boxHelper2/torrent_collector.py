import feedparser
import pymysql
import configparser
import re
import sys

from boxHelper2 import html_parser, torrent
from boxHelper2.html_helper import HtmlHelper
from boxHelper2.torrent import Torrent


class TorrentCollector:

    def __init__(self, url, headers, rss, cycle):
        self.url = url
        self.headers = headers
        self.rss = rss
        self.cycle = cycle
        self.config = configparser.RawConfigParser()
        self.config.read("../config.ini", encoding="utf-8")
        self.db = pymysql.connect(host=self.config.get('global', 'host'), port=int(self.config.get('global', 'port')),
                             user=self.config.get('global', 'user'), passwd=self.config.get('global', 'passwd'), db=self.config.get('global', 'db'), charset='utf8')
        self.cursor = self.db.cursor()

    def __del__(self):
        self.cursor.close()
        self.db.close()

    def collect(self):
        htmlHelper = HtmlHelper(self.url, self.headers)
        raw = htmlHelper.get_source()
        text_by_line = html_parser.filter_tags(raw).split("\n")
        feed = feedparser.parse(self.rss)
        torrent_list = []
        for i in range(len(feed.entries)):
            torrent_list.append(Torrent(str(feed.entries[i].title), str(feed.entries[i].link), str(feed.entries[i].enclosures[0]["href"]), str(feed.entries[i].published_parsed)))
        cycle = sys.maxsize
        indices = []
        if self.cycle == -1:
            for i in range(len(torrent_list)):
                for j in range(len(text_by_line)):
                    if torrent_list[i].title[:50] in text_by_line[j]:
                        indices.append(j)
            indices.sort()
            for i in range(1, len(indices)):
                cycle = min(cycle, indices[i] - indices[i-1])
            if cycle == -1:
                return

        text_by_line = text_by_line[indices[0]:indices[-1]+cycle]
        for i in range(len(torrent_list)):
            for j in range(len(text_by_line)):
                if torrent_list[i].title[:50] in text_by_line[j]:
                    torrent_list[i].set_uploader(text_by_line[j + cycle - 1])
                    t_str = "".join(text_by_line[j:j+cycle])
                    if "KB" in t_str:
                        matcher = re.search(r'\d+\.?\d*KB', t_str)
                        if matcher:
                            torrent_list[i].set_size(float(matcher.group()[:-2])/1024)
                        else:
                            torrent_list[i].set_size(-1)
                    elif "MB" in t_str:
                        matcher = re.search(r'\d+\.?\d*MB', t_str)
                        if matcher:
                            torrent_list[i].set_size(float(matcher.group()[:-2]))
                        else:
                            torrent_list[i].set_size(-1)
                    elif "GB" in t_str:
                        matcher = re.search(r'\d+\.?\d*GB', t_str)
                        if matcher:
                            torrent_list[i].set_size(float(matcher.group()[:-2])*1024)
                        else:
                            torrent_list[i].set_size(-1)
                    elif "TB" in t_str:
                        matcher = re.search(r'\d+\.?\d*TB', t_str)
                        if matcher:
                            torrent_list[i].set_size(float(matcher.group()[:-2])*1024*1024)
                        else:
                            torrent_list[i].set_size(-1)
            print(torrent_list[i])
        return cycle # Remember to update cycle
                    

