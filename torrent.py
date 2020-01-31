class Torrent:

    def __init__(self, detail_link, *, title="", download_link="", uploader="", upload_time=-1, size=-1):
        self.title = title
        self.detail_link = detail_link
        self.download_link = download_link
        self.upload_time = upload_time
        self.uploader = uploader
        self.size = size
        self.promotions = -1

    def __str__(self) -> str:
        return "Title:%s - size:%d - detail_link:%s - download_link:%s - upload_time:%s - promotions:%d"%(self.title, self.size, self.detail_link, self.download_link, self.upload_time, self.promotions)

    def set_size(self, size):
        self.size = size # B

    def set_promotions(self, pro):
        self.promotions = pro