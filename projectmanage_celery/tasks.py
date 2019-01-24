#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import requests, datetime

HOST = 'http://127.0.0.1:8001'

@app.task
def pushMessageToWeChat():
    url = 'http://xmgl.zhugeyingxiao.com/api/pushMessageToWeChat'
    requests.get(url)

# 自动测试
@app.task
def automatic_test():
    url= '{}/api/testCaseDetaile/automatic_test/0'.format(HOST)
    params = {
        'user_id':'10',
        'rand_str':'2be6ba2fa87950c7fb15c5c358722408',
        'timestamp':'1534157927644',
    }
    requests.get(url, params=params)