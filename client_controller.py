import sqlite3
import time
import requests
import json
import configparser


class Deluge:
    def __init__(self) -> None:
        self.count = 0
        self.status_count = 0
        self.config = configparser.RawConfigParser().read("config.ini", encoding="utf-8")
        self.headers = {
            'Content-Type':'application/json'
        }
        self.cookies={}
        self.url=self.config.get('clients', 'deluge_web')
        if self.url.endswith("/"):
            self.url+="json"
        else:
            self.url += "/json"
        self.version = self.get_api_version()
        self.up_bandwidth =  self.config.getint("clients", "up_bandwidth") * 1024 * 1024
        self.potential_torrents = []
        self.download_rate = 0
        self.upload_rate = 0
        self.num_connections = 0
        self.free_space = 0
        self.past_three_rates = [0,0,0,0,0,0] #Three for up, three for down
        self.average_up = 0
        self.average_down = 0


    def get_count(self):
        self.count += 1
        return self.count

    def check_and_login(self):
        data = {"method": "auth.check_session", "params": [], "id": self.get_count()}
        response = json.loads(requests.post(self.url, data=json.dumps(data), headers=self.headers).text)
        if response['result']:
            return True
        else:
            data = {"method": "auth.login", "params": [self.config.get('clients', 'deluge_passwd')], "id": self.get_count()}
            cookies = requests.post(self.url, data=json.dumps(data), headers=self.headers).cookies
            for cookie in cookies:
                self.cookies[cookie.name] = cookie.value
            response = json.loads(requests.post(self.url, data=json.dumps(data), headers=self.headers).text)
            if response['result']:
                return True
            else:
                return False

    def get_api_version(self):
        if not self.check_and_login():
            return -1
        #View deluge hosts
        data = {"method": "web.get_hosts", "params": [], "id": self.get_count()}
        response = json.loads(requests.post(self.url, data=json.dumps(data), headers=self.headers, cookies=self.cookies).text)
        # View deluge host status
        data = {"method": "web.get_host_status", "params": [response['result'][0][0]], "id": self.get_count()}
        response = json.loads(requests.post(self.url, data=json.dumps(data), headers=self.headers, cookies=self.cookies).text)
        return response['result'][-1][0]

    def get_status(self):
        if self.version == 2:
            return
        self.check_and_login()
        self.status_count+=1
        data = {"method":"web.update_ui","params":[["state"],{}],"id": self.get_count()}
        response = json.loads(
            requests.post(self.url, data=json.dumps(data), headers=self.headers, cookies=self.cookies).text)
        # for k in response["result"]["torrents"].keys():
        #     print(k)
        self.download_rate = response["result"]["stats"]["download_rate"]
        self.upload_rate = response["result"]["stats"]["upload_rate"]
        self.num_connections = response["result"]["stats"]["num_connections"]
        self.free_space = response["result"]["stats"]["free_space"]
        self.update_average_rate(self.download_rate, self.upload_rate)
        connection = sqlite3.connect('boxHelper.db')
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO clients_status (client, time, download_rate, upload_rate, connections, free_space) VALUES (?,?,?,?,?,?)",
            ("Deluge", time.time(), self.download_rate, self.upload_rate, self.num_connections, self.free_space))
        connection.commit()
        cursor.close()
        connection.close()
    
    def update_average_rate(self, download, upload):
        self.past_three_rates[self.status_count%3] = upload
        self.past_three_rates[3+self.status_count%3] = download
        self.average_up = sum(self.past_three_rates[:3])//3
        self.average_down = sum(self.past_three_rates[3:])//3


if __name__ == '__main__':
    de = Deluge()
    while True:
        de.get_status()
        if de.upload_rate < de.up_bandwidth * 0.75:
            if de.potential_torrents:
                pass
                # Load and start torrents selected before
            else:
                pass
                #Select potential power torrents
        elif de.upload_rate < de.up_bandwidth * 0.85:
            if de.potential_torrents:
                pass
                # Load and start torrents selected before
            else:
                pass
                #Select potential power torrents
        time.sleep(100)


class ClientController:
    def __init__(self) -> None:
        if self.config.has_option("clients", "deluge_enable") and self.config.get('clients',
                                                                                     'deluge_enable').capitalize() == "TRUE":
            self.deluge = Deluge()




    def get_status(self):
        pass

