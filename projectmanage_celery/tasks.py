#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import requests



@app.task
def timeToRefreshZhgongDianCi():
    print('timeToRefreshZhgongDianCi')
    # url = 'http://127.0.0.1:8000/xiong/article?user_id=1&timestamp=123&rand_str=7e0fc6b6833ebe0347ab6a5945d519ea'
    # requests.get(url)

