import configparser
import logging

from boxHelper2.torrent_collector import TorrentCollector

class TorrentController:

    def start(self):
        config = configparser.RawConfigParser()
        config.read("../config.ini", encoding="utf-8")
        sites_amount = config.getint('sites', 'sites_amount')
        logging.basicConfig(level=logging.DEBUG,
                            filename="../boxHelper.log",
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format='%(asctime)s - %(levelname)s - %(module)s@%(lineno)d : %(message)s')
        logger = logging.getLogger()

        collectors = []
        for i in range(1, sites_amount+1):
            c = TorrentCollector(i, config.get('sites', 'url_' + str(i)),
                                 config.get('sites', 'rss_' + str(i)), config.getint('sites', 'strength_' + str(i)),
                                 config.getint('sites', 'cycle_' + str(i)), logger)
            collectors.append(c)
        for collector in collectors:
            collector.start()

if __name__ == '__main__':
    open("../boxHelper.log","w").close()
    t = TorrentController()
    t.start()