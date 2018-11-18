#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

app = Celery(
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['projectmanage_celery.tasks'],

)
app.conf.enable_utc = False
app.conf.timezone = "Asia/Shanghai"
CELERYD_FORCE_EXECV = True           # 非常重要,有些情况下可以防止死锁
CELERYD_MAX_TASKS_PER_CHILD = 100    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
app.conf.beat_schedule = {

# 每天早上九点到十一点 每隔1小时执行一次
 'pushMessageToWeChat':{
        'task':'projectmanage_celery.tasks.pushMessageToWeChat',
        # 'schedule':30                                   # 单独设置  秒
        # 'schedule': crontab(hour=8, minute=30),
        'schedule': crontab("*", '9', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    },
}
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()