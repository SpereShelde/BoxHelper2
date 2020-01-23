import logging
import threading

import feedparser
import pymysql
import configparser
import re
from collections import Counter
import time
import urllib.request

from boxHelper2 import html_parser, torrent
from boxHelper2.torrent import Torrent


class AutoTorrentCollector(threading.Thread):

    def __init__(self, id, url, headers, rss, strength, cycle_time):
        threading.Thread.__init__(self)
        self.id = id
        self.url = url
        self.headers = headers
        self.rss = rss
        self.strength = strength
        self.pattern_list = []
        self.cycle_time = cycle_time
        self.config = configparser.RawConfigParser()
        self.config.read("../config.ini", encoding="utf-8")

    def run(self):
        while True:
            print("02: id = %d is running" % self.id)
            self.collect()
            time.sleep(self.cycle_time)

    # Collect torrents based on website
    def collect(self):
        ti = int(time.time())
        logging.basicConfig(level=logging.DEBUG,
                            filename='../boxHelper.log',
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
        logger = logging.getLogger()
        #Use rss to get title pattern
        request = urllib.request.Request(url=self.url, headers=self.headers)
        response = urllib.request.urlopen(request)
        time.sleep(1)
        response = urllib.request.urlopen(request)
        raw = response.read().decode('utf-8')  # 获取网站源码
        feed = feedparser.parse(self.rss)  # 从rss读取items

        t = int(time.time())-ti
        print("get source and rss at %d" % t)
        #Automatically find title pattern

        if self.strength == 10:
            pass
            #TorrentCollector()
        elif self.strength == 30:
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
                        while '<' in s:
                            # pattern = s[s.rindex('<'):] + "[^<]*?" + pattern
                            pattern = "%s[^<]*?%s" % (s[s.rindex('<'):], pattern)
                            s = s[:s.rindex('<')]
                    if pattern not in self.pattern_list:
                        self.pattern_list.append(pattern)
            if not self.pattern_list:
                return
            self.strength = 20
        elif self.strength == 20:
            if not self.pattern_list:
                return
        else:
            return
        t = int(time.time()) - ti
        print("get pattern at %d" % t)
        text_by_line = html_parser.filter_tags(raw, self.pattern_list).split("\n")  # 去掉标签然后按行存入list
        feed = feedparser.parse(self.rss)  # 从rss读取items
        torrent_list = []
        feed_titles = {}
        for i in range(len(feed.entries)):
            feed_titles[feed.entries[i].title] = i
        other_str = ""
        pre_torrent = None
        t = int(time.time()) - ti
        print("get rss at %d" % t)
        i = 0
        while i < len(text_by_line):
            if text_by_line[i].startswith("TITLE:"):
                break
            i += 1
        i -= 1
        while i < len(text_by_line):
            if text_by_line[i].startswith("TITLE:"):
                if pre_torrent:
                    if "BFREEH" in other_str:
                        pre_torrent.set_promotions(1)
                    if "KB" in other_str:
                        matcher = re.search(r'\d+\.?\d*KB', other_str)
                        if matcher:
                            pre_torrent.set_size(float(matcher.group()[:-2]) / 1024)
                        else:
                            pre_torrent.set_size(-1)
                    elif "MB" in other_str:
                        matcher = re.search(r'\d+\.?\d*MB', other_str)
                        if matcher:
                            pre_torrent.set_size(float(matcher.group()[:-2]))
                        else:
                            pre_torrent.set_size(-1)
                    elif "GB" in other_str:
                        matcher = re.search(r'\d+\.?\d*GB', other_str)
                        if matcher:
                            pre_torrent.set_size(float(matcher.group()[:-2]) * 1024)
                        else:
                            pre_torrent.set_size(-1)
                    elif "TB" in other_str:
                        matcher = re.search(r'\d+\.?\d*TB', other_str)
                        if matcher:
                            pre_torrent.set_size(float(matcher.group()[:-2]) * 1024 * 1024)
                        else:
                            pre_torrent.set_size(-1)
                    torrent_list.append(pre_torrent)
                    # print(pre_torrent)
                other_str = text_by_line[i][text_by_line[i].index(":END"):]
                title = text_by_line[i][7:text_by_line[i].index(" :END")].strip()
                title = re.compile("\s{2,}").sub(" ", title)
                if title in feed_titles:
                    ind = feed_titles[title]
                    pre_torrent = Torrent(feed.entries[ind].title, detail_link=str(feed.entries[ind].link),
                                          download_link=str(feed.entries[ind].enclosures[0]["href"]),
                                          upload_time=int(time.mktime(feed.entries[ind].published_parsed)))
                else:
                    pre_torrent = Torrent(title)
            else:
                other_str += text_by_line[i]
            i += 1


        db = pymysql.connect(host=self.config.get('global', 'host'),
                             port=self.config.getint('global', 'port'),
                             user=self.config.get('global', 'user'),
                             passwd=self.config.get('global', 'passwd'),
                             db=self.config.get('global', 'db'), charset='utf8')
        cursor = db.cursor()
        get_time = int(time.time())
        for torrent in torrent_list:
            if torrent.detail_link is not "":
                sql = "SELECT get_time FROM torrents_collected WHERE detail_link = '%s'" % (torrent.detail_link)
                try:
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if result:
                        if int(time.time()) - cursor.fetchone()[0] >= 86400 * 2:
                            sql = "UPDATE torrents_collected SET hits = hits + 1 and get_time = %d and promotions = %d WHERE detail_link = '%s'" % (
                            get_time, torrent.promotions, torrent.detail_link)
                        else:
                            sql = "UPDATE torrents_collected SET hits = hits + 1 and promotions = %d WHERE detail_link = '%s'" % (
                            torrent.promotions, torrent.detail_link)
                        try:
                            cursor.execute(sql)
                            db.commit()
                        except:
                            logger.error("Cannot update torrent.")
                            db.rollback()
                    else:
                        sql = "INSERT INTO torrents_collected (title, size, promotions, detail_link, download_link, upload_time, hits, get_time) VALUES ('%s',%d,%d,'%s','%s',%d,%d,%d)" \
                              % (torrent.title, torrent.size, torrent.promotions, torrent.detail_link,
                                 torrent.download_link, torrent.upload_time, 1, get_time)
                        try:
                            cursor.execute(sql)
                            db.commit()
                        except:
                            logger.error("Cannot insert torrent.")
                            db.rollback()
                except:
                    logger.error("Cannot query torrent.")
            else:
                # torrent info not completed
                sql = "SELECT detail_link FROM torrents_collected WHERE title = '%s'" % (torrent.title)
                try:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    if results:
                        if len(results) > 1:
                            logger.info("Get same name torrents. Not Update")
                        else:
                            if int(time.time()) - cursor.fetchone()[0][0] >= 86400 * 2:
                                sql = "UPDATE torrents_collected SET hits = hits + 1 and get_time = %d and promotions = %d WHERE title = '%s'" % (
                                get_time, torrent.promotions, torrent.title)
                            else:
                                sql = "UPDATE torrents_collected SET hits = hits + 1 and promotions = %d WHERE title = '%s'" % (
                                torrent.promotions, torrent.title)
                            try:
                                cursor.execute(sql)
                                db.commit()
                            except:
                                logger.error("Cannot update torrent.")
                                db.rollback()
                    else:
                        sql = "INSERT INTO torrents_collected (title, size, promotions, detail_link, download_link, upload_time, hits, get_time) VALUES ('%s',%d,%d,'%s','%s',%d,%d,%d)" \
                              % (torrent.title, torrent.size, torrent.promotions, torrent.detail_link,
                                 torrent.download_link, torrent.upload_time, 1, get_time)
                        try:
                            cursor.execute(sql)
                            db.commit()
                        except:
                            logger.error("Cannot insert torrent.")
                            db.rollback()
                except:
                    logger.error("Cannot query torrent.")
        cursor.close()
        db.close()
        t = int(time.time()) - ti
        print("get db at %d" % t)


