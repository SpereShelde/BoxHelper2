from html_helper import HtmlHelper
from torrent import Torrent
import html_parser
import feedparser
import pymysql
import configparser
import re
import sys

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
                    if torrent_list[i].title in text_by_line[j]:
                        indices.append(j)
            indices.sort()
            for i in range(1, len(indices)):
                cycle = min(cycle, indices[i] - indices[i-1])
            if cycle == -1:
                return
        else:
            text_by_line = text_by_line[indices[0]:indices[-1]+cycle]
            for i in range(len(torrent_list)):
                for j in range(len(text_by_line)):
                    if torrent_list[i].title in text_by_line[j]:
                        torrent.set_uploader(text_by_line[j+cycle-1])
                        t_str = "".join(text_by_line[index:index+j])
                        if "KB" in t_str:
                            re_size = re.compile('\d+\.?\d*KB')
                            size_str = re_size.match(t_str).group()
                            if size_str is not None:
                                torrent.set_size(float(size_str[:-2]))
                        elif "MB" in t_str:
                            re_size = re.compile('\d+\.?\d*MB')
                            size_str = re_size.match(t_str).group()
                            if size_str is not None:
                                torrent.set_size(float(size_str[:-2]))
                        elif "GB" in t_str:
                            re_size = re.compile('\d+\.?\d*GB')
                            size_str = re_size.match(t_str).group()
                            if size_str is not None:
                                torrent.set_size(float(size_str[:-2]))
                        elif "TB" in t_str:
                            re_size = re.compile('\d+\.?\d*TB')
                            size_str = re_size.match(t_str).group()
                            if size_str is not None:
                                torrent.set_size(float(size_str[:-2]))
                    print(torrent)
        return cycle # Remember to update cycle
                    



        


if __name__ == '__main__':
    url = "https://pt.m-team.cc/movie.php"
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'c_lang_folder=en; __cfduid=ddd408e74ffec1659152b036f752cfd181579131458; tp=MjUwMWM0ZWI2NmVkOTdlNTIxMTI0MDNhNGJlOGQ4NWIzOTI4NTkwNg%3D%3D',
    }
    rss = "https://pt.m-team.cc/torrentrss.php?https=1&rows=50&cat401=1&cat419=1&cat420=1&cat421=1&cat439=1&linktype=dl&passkey=a572aafaf362467e9efc67bb07d4dcfb"
    t = TorrentCollector(url, headers, rss, -1)
    t.collect()