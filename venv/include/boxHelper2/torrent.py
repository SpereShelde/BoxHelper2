class Torrent:

    def __init__(self, title, detail_link, download_link, upload_time):
        self.title = title
        self.detail_link = detail_link
        self.download_link = download_link
        self.upload_time = upload_time

    def __str__(self) -> str:
        return "Title:%s - size:%d - detail_link:%s - download_link:%s - uploader:%s - upload_time:%s "%(self.title, self.size, self.detail_link, self.download_link, self.uploader, self.upload_time)

    def set_size(self, size):
        self.size = size # MB
        
    def set_uploader(self, uploader):
        self.uploader = uploader
