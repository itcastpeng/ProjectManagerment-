#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import requests, datetime



@app.task
def pushMessageToWeChat():
    url = 'http://xmgl.zhugeyingxiao.com/api/pushMessageToWeChat'
    requests.get(url)