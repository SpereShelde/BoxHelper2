
if __name__ == '__main__':
    open("boxHelper.log", "w").close()
    config = configparser.RawConfigParser()
    logging.basicConfig(level=logging.DEBUG,
                        filename="boxHelper.log",
                        datefmt='%Y/%m/%d %H:%M:%S',
                        format='%(asctime)s - %(levelname)s - %(module)s@%(lineno)d : %(message)s')
    logger = logging.getLogger()
    config.read("config.ini", encoding="utf-8")
    c = TorrentCollector(1, config.get('sites', 'url_' + str(1)),
                         config.get('sites', 'rss_' + str(1)), config.getint('sites', 'strength_' + str(1)),
                         config.getint('sites', 'cycle_' + str(1)), logger)
    c.run()




[sites]
sites_amount = 2

url_1 = https://hdsky.me/torrents.php
cookie_1 = c_secure_ssl=eWVhaA%3D%3D; c_lang_folder=en; __cfduid=dc50e1f6e6b50730d3c32a2216c7848d41572723896; UM_distinctid=16e2da65add587-0ea53057c90541-123b6a5a-1aeaa0-16e2da65ade8db; CNZZDATA5476511=cnzz_eid%3D1576701398-1542419927-%26ntime%3D1579794522; c_secure_uid=ODk1MTI%3D; c_secure_pass=606bda82a08fbaa84fa8b64b625a2436; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D
rss_1 = https://hdsky.me/torrentrss.php?rows=40&linktype=dl&passkey=4c5c0c98fea40d18f35091a5253e90b4
strength_1 = 20
#Strength: searching strength. 20 means full auto inspect; 10 means limited inpect based on rss
cycle_1 = 20

#Cycle: cycle time in seconds

url_2 = https://pt.m-team.cc/movie.php
cookie_2 = c_lang_folder=en; __cfduid=ddd408e74ffec1659152b036f752cfd181579131458; tp=MjUwMWM0ZWI2NmVkOTdlNTIxMTI0MDNhNGJlOGQ4NWIzOTI4NTkwNg%3D%3D
rss_2 = https://pt.m-team.cc/torrentrss.php?https=1&rows=50&cat401=1&cat419=1&cat420=1&cat421=1&cat439=1&linktype=dl&passkey=fcbfa9e5fb83b0f4b056b7d07d0a3008
strength_2 = 20
#Strength: searching strength. 20 means full auto inspect; 10 means limited inpect based on rss
cycle_2 = 20
#Cycle: cycle time in seconds


