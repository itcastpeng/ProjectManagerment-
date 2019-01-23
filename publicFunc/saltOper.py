# 调用salt api 进行操作
import requests


class SaltOper:

    def __init__(self):
        self.token = None
        self.login()

    def login(self):
        url = 'https://192.168.10.110:8001/login'
        headers = {
            'Accept': 'application/json',
        }
        post_data = {'username': 'saltapi', 'password': 'saltapi@2018', 'eauth': 'pam'}

        ret = requests.post(url, post_data, headers=headers, verify=False)
        print('login_ret  -->', ret.json())
        self.token = ret.json()['return'][0]['token']

    def cmdRun(self, tgt, cmd):
        url = 'https://192.168.10.110:8001/'
        headers = {
            'Accept': 'application/json',
            'X-Auth-Token': self.token,
        }

        post_data = {
            'client': 'local',
            'tgt': tgt,
            'fun': 'cmd.run',
            'arg': cmd,
        }

        # print('post_data -->', post_data)
        ret = requests.post(url, post_data, headers=headers, verify=False)
        # print('zhixing  -->', ret.json())

        return ret.json()