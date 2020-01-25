import configparser
import logging

from torrent_collector import TorrentCollector


class TorrentController:

    def __init__(self) -> None:
        self.collectors = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="boxHelper.log",
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format='%(asctime)s - %(levelname)s - %(module)s@%(lineno)d : %(message)s')
        self.logger = logging.getLogger()

    def stop(self):
        self.logger.info("Collectors will stop after their current run.")
        for collector in self.collectors:
            collector.stop()

    def is_alive(self):
        if not self.collectors:
            return False
        for collector in self.collectors:
            if not collector.is_alive():
                return False
        return True

    def start(self):
        open("boxHelper.log", "w").close()
        config = configparser.RawConfigParser()
        config.read("config.ini", encoding="utf-8")
        sites_amount = config.getint('sites', 'sites_amount')
        for i in range(1, sites_amount+1):
            c = TorrentCollector(i, config.get('sites', 'url_' + str(i)),
                                 config.get('sites', 'rss_' + str(i)), config.getint('sites', 'strength_' + str(i)),
                                 config.getint('sites', 'cycle_' + str(i)), self.logger)
            self.collectors.append(c)

        for collector in self.collectors:
            collector.start()

tc = TorrentController()
