import urllib.request

class HtmlHelper:

    url = ""
    headers = {}

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def get_source(self):
        request = urllib.request.Request(url=self.url, headers=self.headers)
        response = urllib.request.urlopen(request)
        
        return response.read().decode('utf-8')