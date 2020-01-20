class TorrentController:

    def start(self):
        config = configparser.RawConfigParser()
        config.read("../config.ini", encoding="utf-8")
        sites_amount = config.get('sites', 'sites_amount')
        for i in range(len(sites_amount)):
            pass

if __name__ == '__main__':
    a = "He\\'s a Woman, She\\'s a Man 1994 NTSC DVD9-ADC"
    print(str(a))
    print(repr(a))
