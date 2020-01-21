import feedparser
import pymysql
import configparser
import re
from collections import Counter
import time

from boxHelper2 import html_parser, torrent
from boxHelper2.html_helper import HtmlHelper
from boxHelper2.torrent import Torrent


class TorrentCollector2:

    def __init__(self, url, headers, rss):
        self.url = url
        self.headers = headers
        self.rss = rss
        self.config = configparser.RawConfigParser()
        self.config.read("../config.ini", encoding="utf-8")
        self.db = pymysql.connect(host=self.config.get('global', 'host'), port=int(self.config.get('global', 'port')),
                                  user=self.config.get('global', 'user'), passwd=self.config.get('global', 'passwd'),
                                  db=self.config.get('global', 'db'), charset='utf8')
        self.cursor = self.db.cursor()


    def __del__(self):
        self.cursor.close()
        self.db.close()

    # Collect torrents based on website
    def collect(self):
        #Use rss to get title pattern

        re_title = re.compile('')  # HTML标签

        htmlHelper = HtmlHelper(self.url, self.headers)
        raw = htmlHelper.get_source()  # 获取网站源码
        feed = feedparser.parse(self.rss)  # 从rss读取items
        torrent_list = []
        pattern = ""
        for i in range(len(feed.entries)):
            if feed.entries[i].title in raw:
                index = raw.index(feed.entries[i].title) - 1
                pattern = "(.*?)"+raw[index]
                while index >= 0 and raw[index] != " ":
                    pattern = raw[index]+pattern
                    index -= 1
                reg = re.compile('\S*')
                strs = reg.findall(raw[index-100:index])
                for i in reversed(range(len(strs))):
                    s = strs[i]
                    while '><' in s:
                        pattern = s[s.rindex('><')+1:] + "[^<]*?" + pattern
                        s = s[:s.rindex('><')]
                # for _ in range(pattern.count("<") - pattern.count(">")-1):
                #     pattern = pattern+'[^<]*?>'
                break
        print(pattern)
        print("!!!")
        text_by_line = html_parser.filter_tags(raw).split("\n")  # 去掉标签然后按行存入list
        feed = feedparser.parse(self.rss)  # 从rss读取items
        torrent_list = []
        for i in range(len(feed.entries)):
            torrent_list.append(Torrent(str(feed.entries[i].title), str(feed.entries[i].link),
                                        str(feed.entries[i].enclosures[0]["href"]),
                                        time.strftime("%Y-%m-%d %H:%M:%S", feed.entries[i].published_parsed)))
        indices = []  # 存放匹配的title
        for i in range(len(torrent_list)):
            for j in range(len(text_by_line)):
                if torrent_list[i].title[:50] in text_by_line[j]:
                    indices.append(j)
        indices.sort()  # 排序
        cycles = []
        for i in range(1, len(indices)):
            cycles.append(indices[i] - indices[i - 1])
            # 获得title间的差值
        cycle = Counter(cycles).most_common(1)[0][0]
        # 出现最多次数的差值是循环行数
        for i in range(len(torrent_list)):
            for j in range(len(indices)):
                if torrent_list[i].title[:50] in text_by_line[indices[j]]:
                    if "BFreeH" in text_by_line[indices[j]]:
                        torrent_list[i].set_promotions(1)
                    t_str = "".join(text_by_line[indices[j]:indices[j] + cycle])
                    # 在title后cycle行内正则获取种子大小
                    if "KB" in t_str:
                        matcher = re.search(r'\d+\.?\d*KB', t_str)
                        if matcher:
                            torrent_list[i].set_size(float(matcher.group()[:-2]) / 1024)
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
                            torrent_list[i].set_size(float(matcher.group()[:-2]) * 1024)
                        else:
                            torrent_list[i].set_size(-1)
                    elif "TB" in t_str:
                        matcher = re.search(r'\d+\.?\d*TB', t_str)
                        if matcher:
                            torrent_list[i].set_size(float(matcher.group()[:-2]) * 1024 * 1024)
                        else:
                            torrent_list[i].set_size(-1)
            print(torrent_list[i])
            # sql = "INSERT INTO torrents_collected (title, AGE, SEX) VALUES (%s,%s,%s)" % ('Mac', 20, 'boy')

            # try:
            #     # 执行sql语句
            #     cursor.execute(sql)
            #     # 提交到数据库执行
            #     db.commit()
            # except:
            #     # 如果发生错误则回滚
            #     db.rollback()
            # print(torrent_list[i])

