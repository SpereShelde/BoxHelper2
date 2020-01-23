import configparser

from boxHelper2.auto_torrent_collector import AutoTorrentCollector


class TorrentController():

    def start(self):
        config = configparser.RawConfigParser()
        config.read("../config.ini", encoding="utf-8")
        sites_amount = config.getint('sites', 'sites_amount')
        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        collectors = []
        for i in range(1, sites_amount+1):
            headers['Cookie'] = config.get('sites', 'cookie_' + str(i))
            c = AutoTorrentCollector(i, config.get('sites', 'url_' + str(i)), headers,
                                     config.get('sites', 'rss_' + str(i)), config.getint('sites', 'strength_' + str(i)),
                                     config.getint('sites', 'cycle_' + str(i)))
            collectors.append(c)
        print("01: %d collectors" % len(collectors))
        for collector in collectors:
            collector.run()

if __name__ == '__main__':
    t = TorrentController()
    t.start()
