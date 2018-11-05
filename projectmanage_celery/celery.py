#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com


from __future__ import absolute_import, unicode_literals

from celery import Celery
from celery.schedules import crontab

app = Celery(
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['projectmanage_celery.tasks'],
    CELERY_TIMEZONE = 'Asia/Shanghai'
)

app.conf.beat_schedule = {

    # # 配置每隔一个小时执行一次
    # 'CheckWenda': {  # 此处的命名不要用 tasks 开头,否则会报错
    #     'task': 'wenda_celery_project.tasks.CheckWenda',  # 要执行的任务函数名
    #     'schedule': crontab("*", '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    #     # 'args': (2, 2),                                     # 传递的参数
    # },


    'pushMessageToWeChat':{
        'task':'projectmanage_celery.tasks.pushMessageToWeChat',
        # 'schedule':30                                # 秒
        # 'schedule': crontab("30", '19', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
        'schedule': crontab(hour=19, minute=40),  # 此处跟 linux 中 crontab 的格式一样
    }

}

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
    # CELERY_TIMEZONE = 'Asia/Shanghai'
)

if __name__ == '__main__':
    app.start()
