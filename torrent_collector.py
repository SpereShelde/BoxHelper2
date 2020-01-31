import threading

import feedparser
import configparser
import re
import time
import urllib.request
import sqlite3
import sys

import html_parser
from torrent import Torrent


class TorrentCollector(threading.Thread):

    def is_alive(self):
        return super().is_alive()

    def __init__(self, id, url, rss, strength, cycle_time, logger):
        threading.Thread.__init__(self)
        self.id, self.url, self.rss, self.strength, self.cycle_time, self.logger = id, url, rss, strength, cycle_time, logger
        self.pattern_list = []
        self.config = configparser.RawConfigParser()
        self.config.read("config.ini", encoding="utf-8")
        self.headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.headers['Cookie'] = self.config.get('sites', 'cookie_' + str(id))
        self.should_running = True
        self.prefix = ''
        self.detail_suffix = ''

    def stop(self):
        self.should_running = False

    def run(self):
        count = 1
        while self.should_running:
            record_time = int(time.time())
            self.logger.info("Torrent collector number %d starts the %dth run" % (self.id, count))
            self.collect()
            record_time = int(time.time()) - record_time
            self.logger.info("Torrent collector number %d end the %dth run and will sleep for %d seconds" % (
            self.id, count, self.cycle_time - record_time))
            sleep_time = self.cycle_time - record_time
            time.sleep(sleep_time if sleep_time > 0 else 5)
            count += 1
        self.logger.info("Torrent collector number %d stopped" % self.id)

    def collect(self):
        request = urllib.request.Request(url=self.url, headers=self.headers)
        response = urllib.request.urlopen(request)
        raw = response.read().decode('utf-8')  # 获取网站源码
        feed = feedparser.parse(self.rss)  # 从rss读取items

        if self.strength == 10:

            text_by_line = html_parser.filter_tags(raw, []).split("\n")  # 去掉标签然后按行存入list

            torrent_list = []
            for i in range(len(feed.entries)):
                torrent_list.append(Torrent(detail_link= feed.entries[i].link, title=feed.entries[i].title, download_link=feed.entries[i].enclosures[0]["href"],
                                            upload_time=time.mktime(feed.entries[i].published_parsed), size=feed.entries[i].enclosures[0]["length"], uploader=feed.entries[i].author))
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
                        self.find_pro(torrent_list[i], t_str)

            connection = sqlite3.connect('boxHelper.db')
            cursor = connection.cursor()
            get_time = int(time.time())
            for torrent in torrent_list:
                self.insert_torrent(torrent, get_time, connection, cursor)
            cursor.close()
            connection.close()
            return
        elif self.strength == 20:
            connection = sqlite3.connect('boxHelper.db')
            cursor = connection.cursor()
            result = None
            try:
                cursor.execute("SELECT detail_pattern, prefix, detail_suffix FROM patterns WHERE site_id = ?", (self.id,))
                result = cursor.fetchone()
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Cannot query pattern of %d" % self.id)
            if result:
                cursor.close()
                connection.close()
                self.pattern_list = result[0].split("@Box#Helper@")
                self.prefix = result[1]
                self.detail_suffix = result[2]
            else:

                for i in range(len(feed.entries)):
                    link = feed.entries[i].link
                    while link not in raw:
                        try:
                            link = link[link.index('/')+1:]
                        except IndexError as e:
                            pass
                    if link in raw:
                        self.prefix = feed.entries[i].link[:feed.entries[i].link.index(link)]
                        start = raw.index(link) - 1
                        end = start+1+len(link)
                        if raw[start] != '"':
                            self.logger.info("Please contact author.")
                        if raw[end] != '"':
                            # sufix
                            self.detail_suffix = html_parser.replace_char_entity(raw[end:raw.find('"', end)])

                        pre_index = raw[:start].rindex('<')
                        pattern = '<[^<>]*?href="(?P<link>%s[^"]*)"[^<>]*?>' % link[:3]
                        reg = re.compile('\S+')
                        strs = reg.findall(raw[pre_index - 100:pre_index])
                        for i in reversed(range(len(strs))):
                            s = strs[i]
                            while '<' in s:
                                pattern = '%s[^<]*?%s' % (s[s.rindex('<'):], pattern)
                                s = s[:s.rindex('<')]
                        #
                        # index = raw.index(link) - 1
                        # pattern = "(.*?)"+raw[index]
                        # while index >= 0 and raw[index] != " ":
                        #     pattern = raw[index]+pattern
                        #     index -= 1
                        # reg = re.compile('\S*')
                        # strs = reg.findall(raw[index-100:index])
                        # for i in reversed(range(len(strs))):
                        #     s = strs[i]
                        #     while '<' in s:
                        #         pattern = "%s[^<]*?%s" % (s[s.rindex('<'):], pattern)
                        #         s = s[:s.rindex('<')]
                        if pattern not in self.pattern_list:
                            self.pattern_list.append(pattern)
                if not self.pattern_list:
                    return
                print('@Box#Helper@'.join(self.pattern_list))
                cursor.execute("INSERT INTO patterns (detail_pattern, prefix, site_id, detail_suffix) VALUES (?, ?, ?, ?)", ('@Box#Helper@'.join(self.pattern_list), self.prefix, self.id, self.detail_suffix))
                connection.commit()
                cursor.close()
                connection.close()
        else:
            return

        #feed_links is a dic restores link:index
        feed_links = {}
        for i in range(len(feed.entries)):
            feed_links[feed.entries[i].link.replace(self.prefix, '').replace(self.detail_suffix, '')] = i
        #text_by_line is a list restores texts from html
        text_by_line = html_parser.filter_tags(raw, self.pattern_list).split("\n")

        for t in text_by_line:
            print(t)

        #Locate the first torrent item
        i = 0
        while i < len(text_by_line):
            if text_by_line[i].strip().startswith("BLINKHSTART:"):
                break
            i += 1
        torrent_list = []
        pre_torrent = None
        other_str = ""
        while i < len(text_by_line):
            # b =text_by_line[i].strip()
            if text_by_line[i].strip().startswith("BLINKHSTART:"):
                ind = text_by_line[i].index(":ENDBLINKH")
                if other_str == "":
                    other_str = text_by_line[i][ind:]
                detail = text_by_line[i][13:ind].strip()
                real_detail = detail.replace(self.detail_suffix, '')
                # a =self.prefix+real_detail
                if pre_torrent and pre_torrent.detail_link != self.prefix+real_detail:
                    self.find_pro(pre_torrent, other_str)
                    torrent_list.append(pre_torrent)
                    other_str = text_by_line[i][ind:]
                # detail = re.compile("\s{2,}").sub(" ", detail)
                if real_detail in feed_links:
                    ind = feed_links[real_detail]
                    pre_torrent = Torrent(detail_link=feed.entries[ind].link, title=feed.entries[ind].title,
                                          download_link=feed.entries[ind].enclosures[0]["href"],
                                          upload_time=int(time.mktime(feed.entries[ind].published_parsed)), size=feed.entries[ind].enclosures[0]["length"], uploader=feed.entries[ind].author)
                    # other_str = text_by_line[i][ind:]
                else:
                    pre_torrent = Torrent(self.prefix+real_detail)
            else:
                other_str += text_by_line[i]
            i += 1

        connection = sqlite3.connect('boxHelper.db')
        cursor = connection.cursor()
        get_time = int(time.time())
        for torrent in torrent_list:
            self.insert_torrent(torrent, get_time, connection, cursor)
        cursor.close()
        connection.close()

    def insert_torrent(self, torrent, get_time, connection, cursor):
        if torrent.detail_link:
            result = None
            try:
                cursor.execute("SELECT get_time FROM torrents_collected WHERE detail_link = ?", (torrent.detail_link,))
                result = cursor.fetchone()
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Cannot query torrent %s" % torrent.detail_link)
            if result:
                if int(time.time()) - result[0] >= 86400 * 2:
                    try:
                        cursor.execute("UPDATE torrents_collected SET get_time = ? and promotions = ? WHERE detail_link = ?", (get_time, torrent.promotions, torrent.detail_link))
                        connection.commit()
                    except Exception as e:
                        self.logger.error(e)
                        self.logger.error("Cannot update torrent %s" % torrent.detail_link)
                        connection.rollback()
                else:
                    try:
                        cursor.execute("UPDATE torrents_collected SET promotions = ? WHERE detail_link = ?", (torrent.promotions, torrent.detail_link))
                        connection.commit()
                    except Exception as e:
                        self.logger.error(e)
                        self.logger.error("Cannot update torrent %s" % torrent.detail_link)
                        connection.rollback()

            else:
                try:
                    cursor.execute("INSERT INTO torrents_collected (title, size, promotions, detail_link, download_link, upload_time, get_time, uploader) VALUES (?,?,?,?,?,?,?,?)",
                                   (torrent.title, torrent.size, torrent.promotions, torrent.detail_link, torrent.download_link, torrent.upload_time, get_time, torrent.uploader))
                    connection.commit()
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error("Cannot insert torrent %s" % torrent.title)
                    connection.rollback()
        else:
            self.logger.info("Torrent doesn't have detail_link")

    def find_pro(self, torrent, str):
        if "BFREEH" in str:
            torrent.set_promotions(1)
        # 在title后cycle行内正则获取种子大小
        # if "GB" in str:
        #     matcher = re.search(r'\d+\.?\d*GB', str)
        #     if matcher:
        #         torrent.set_size(float(matcher.group()[:-2]) * 1024)
        #     else:
        #         torrent.set_size(-1)
        # elif "MB" in str:
        #     matcher = re.search(r'\d+\.?\d*MB', str)
        #     if matcher:
        #         torrent.set_size(float(matcher.group()[:-2]))
        #     else:
        #         torrent.set_size(-1)
        # elif "KB" in str:
        #     matcher = re.search(r'\d+\.?\d*KB', str)
        #     if matcher:
        #         torrent.set_size(float(matcher.group()[:-2]) / 1024)
        #     else:
        #         torrent.set_size(-1)
        #
        # elif "TB" in str:
        #     matcher = re.search(r'\d+\.?\d*TB', str)
        #     if matcher:
        #         torrent.set_size(float(matcher.group()[:-2]) * 1024 * 1024)
        #     else:
        #         torrent.set_size(-1)
