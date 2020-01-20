import urllib.request
import http.cookiejar

if __name__ == "__main__":

    url = "https://pt.m-team.cc/movie.php"
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'c_lang_folder=en; __cfduid=ddd408e74ffec1659152b036f752cfd181579131458; tp=MjUwMWM0ZWI2NmVkOTdlNTIxMTI0MDNhNGJlOGQ4NWIzOTI4NTkwNg%3D%3D',
    }
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    print(response.read().decode('utf-8'))