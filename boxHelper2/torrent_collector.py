import threading

import feedparser
import pymysql
import configparser
import re
import time
import urllib.request

import sys

from boxHelper2 import html_parser
from boxHelper2.torrent import Torrent


class TorrentCollector(threading.Thread):

    def __init__(self, id, url, rss, strength, cycle_time, logger):
        threading.Thread.__init__(self)
        self.id, self.url, self.rss, self.strength, self.cycle_time, self.logger = id, url, rss, strength, cycle_time, logger
        self.pattern_list = []
        self.config = configparser.RawConfigParser()
        self.config.read("../config.ini", encoding="utf-8")
        self.headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.headers['Cookie'] = self.config.get('sites', 'cookie_' + str(id))

    def run(self):
        count = 1
        while True:
            record_time = int(time.time())
            self.logger.info("Torrent collector number %d starts the %dth run" % (self.id, count))
            self.collect()
            record_time = int(time.time()) - record_time
            self.logger.info("Torrent collector number %d end the %dth run and will sleep for %d seconds" % (
            self.id, count, self.cycle_time - record_time))
            time.sleep(self.cycle_time - record_time)
            count += 1

    def collect(self):
        request = urllib.request.Request(url=self.url, headers=self.headers)
        response = urllib.request.urlopen(request)
        raw = response.read().decode('utf-8')  # 获取网站源码
        feed = feedparser.parse(self.rss)  # 从rss读取items

        if self.strength == 10:

            text_by_line = html_parser.filter_tags(raw, []).split("\n")  # 去掉标签然后按行存入list
            torrent_list = []
            for i in range(len(feed.entries)):
                torrent_list.append(Torrent(feed.entries[i].title, detail_link= feed.entries[i].link,
                                            download_link=feed.entries[i].enclosures[0]["href"],
                                            upload_time=time.mktime(feed.entries[i].published_parsed)))
            indices = []  # 存放匹配的title
            for i in range(len(torrent_list)):
                for j in range(len(text_by_line)):
                    if torrent_list[i].title[:50] in text_by_line[j]:
                        indices.append(j)
            indices.sort()  # 排序
            cycle = sys.maxsize
            for i in range(1, len(indices)):
                cycle = min(cycle,indices[i] - indices[i - 1])
                # 最小的差值是最小循环行数
            for i in range(len(torrent_list)):
                for j in range(len(indices)):
                    if torrent_list[i].title[:50] in text_by_line[indices[j]]:
                        t_str = "".join(text_by_line[indices[j]:indices[j] + cycle])
                        find_size_pro(torrent_list[i], t_str)

            db = pymysql.connect(host=self.config.get('global', 'host'),
                                 port=self.config.getint('global', 'port'),
                                 user=self.config.get('global', 'user'),
                                 passwd=self.config.get('global', 'passwd'),
                                 db=self.config.get('global', 'db'), charset='utf8')
            cursor = db.cursor()
            get_time = int(time.time())
            for torrent in torrent_list:
                insert_torrent(torrent, db, cursor, self.logger, get_time)
            cursor.close()
            db.close()
            return
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
                self.logger.info("Cannot find any pattern, return.")
                return
        else:
            return
        torrent_list = []
        feed_titles = {}
        for i in range(len(feed.entries)):
            feed_titles[feed.entries[i].title] = i
        other_str = ""
        pre_torrent = None
        i = 0

        text_by_line = html_parser.filter_tags(raw, self.pattern_list).split("\n")  # 去掉标签然后按行存入list
        while i < len(text_by_line):
            if text_by_line[i].startswith("TITLE:"):
                break
            i += 1
        i -= 1
        while i < len(text_by_line):
            if text_by_line[i].startswith("TITLE:"):
                if pre_torrent:
                    find_size_pro(pre_torrent, other_str)
                    torrent_list.append(pre_torrent)
                other_str = text_by_line[i][text_by_line[i].index(":END"):]
                title = text_by_line[i][7:text_by_line[i].index(" :END")].strip()
                title = re.compile("\s{2,}").sub(" ", title)
                if title in feed_titles:
                    ind = feed_titles[title]
                    pre_torrent = Torrent(feed.entries[ind].title, detail_link=feed.entries[ind].link,
                                          download_link=feed.entries[ind].enclosures[0]["href"],
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
            insert_torrent(torrent, db, cursor, self.logger, get_time)
        cursor.close()
        db.close()

def insert_torrent(torrent, db, cursor, logger,  get_time):
    sql = "SELECT get_time FROM torrents_collected WHERE detail_link = '%s'" % torrent.detail_link
    result = None
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except:
        logger.error("Cannot query torrent %s" % torrent.detail_link)
    if result:
        if int(time.time()) - result[0] >= 86400 * 2:
            sql = "UPDATE torrents_collected SET hits = hits + 1 and get_time = %d and promotions = %d WHERE detail_link = '%s'" % (
                get_time, torrent.promotions, torrent.detail_link)
        else:
            sql = "UPDATE torrents_collected SET hits = hits + 1 and promotions = %d WHERE detail_link = '%s'" % (
                torrent.promotions, torrent.detail_link)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            logger.error("Cannot update torrent %s" % torrent.detail_link)
            db.rollback()
    else:


        # insert情况不全



        sql = "SELECT get_time FROM torrents_collected WHERE title = '%s'" % torrent.title
        result = None
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
        except:
            logger.error("Cannot query torrent %s" % torrent.title)
        if not result:
            sql = "INSERT INTO torrents_collected (title, size, promotions, detail_link, download_link, upload_time, hits, get_time) VALUES ('%s',%d,%d,'%s','%s',%d,%d,%d)" \
                  % (torrent.title, torrent.size, torrent.promotions, torrent.detail_link,
                     torrent.download_link, torrent.upload_time, 1, get_time)
            try:
                cursor.execute(sql)
                db.commit()
            except:
                logger.error("Cannot insert torrent %s" % torrent.title)
                db.rollback()
        elif len(result) == 1:
            if int(time.time()) - int(result[0][0]) >= 86400 * 2:
                sql = "UPDATE torrents_collected SET hits = hits + 1 and get_time = %d and promotions = %d WHERE title = '%s'" % (
                    get_time, torrent.promotions, torrent.title)
            else:
                sql = "UPDATE torrents_collected SET hits = hits + 1 and promotions = %d WHERE title = '%s'" % (
                    torrent.promotions, torrent.title)
            try:
                cursor.execute(sql)
                db.commit()
            except:
                logger.error("Cannot update torrent %s" % torrent.title)
                db.rollback()
        else:
            #DO nothing
            logger.info("Same-name torrents exist. Cannot update torrent %s" % torrent.title)

def find_size_pro(torrent, str):
    if "BFREEH" in str:
        torrent.set_promotions(1)
    # 在title后cycle行内正则获取种子大小
    if "KB" in str:
        matcher = re.search(r'\d+\.?\d*KB', str)
        if matcher:
            torrent.set_size(float(matcher.group()[:-2]) / 1024)
        else:
            torrent.set_size(-1)
    elif "MB" in str:
        matcher = re.search(r'\d+\.?\d*MB', str)
        if matcher:
            torrent.set_size(float(matcher.group()[:-2]))
        else:
            torrent.set_size(-1)
    elif "GB" in str:
        matcher = re.search(r'\d+\.?\d*GB', str)
        if matcher:
            torrent.set_size(float(matcher.group()[:-2]) * 1024)
        else:
            torrent.set_size(-1)
    elif "TB" in str:
        matcher = re.search(r'\d+\.?\d*TB', str)
        if matcher:
            torrent.set_size(float(matcher.group()[:-2]) * 1024 * 1024)
        else:
            torrent.set_size(-1)
