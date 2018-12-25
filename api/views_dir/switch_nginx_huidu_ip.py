from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from api.forms.role import AddForm, UpdateForm, SelectForm
import json
from api.views_dir.permissions import init_data
import os
import requests


# cerf  token验证 用户展示模块
@csrf_exempt
def switch_nginx_huidu_ip(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        print('os.getcwd()-->', os.getcwd())
        print('request.META -->', request.META)
        old_ip = json.loads(open(os.path.join(os.getcwd() + '/api/data/switch_nginx_huidu_ip.json')).read())['ip']

        if request.META.get('HTTP_X_FORWARDED_FOR'):
            new_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            new_ip = request.META['REMOTE_ADDR']

        response.code = 200
        response.data = {
            'new_ip': new_ip,
            'old_ip': old_ip
        }
        response.msg = "获取成功"

    return JsonResponse(response.__dict__)


#  增删改
#  csrf  token验证
@csrf_exempt
def switch_nginx_huidu_ip_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "update":
            old_ip = json.loads(open(os.path.join(os.getcwd() + '/api/data/switch_nginx_huidu_ip.json')).read())['ip']

            if request.META.get('HTTP_X_FORWARDED_FOR'):
                new_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                new_ip = request.META['REMOTE_ADDR']

            switch_ip(old_ip, new_ip)

            data = {
                "ip": new_ip
            }
            open(os.path.join(os.getcwd() + '/api/data/switch_nginx_huidu_ip.json'), 'w').write(json.dumps(data))

            response.code = 200
            response.msg = "修改成功"
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)


def switch_ip(old_ip, new_ip):
    url = 'https://192.168.10.110:8001/login'
    headers = {
        'Accept': 'application/json',
    }
    post_data = {'username': 'saltapi', 'password': 'saltapi@2018', 'eauth': 'pam'}

    ret = requests.post(url, post_data, headers=headers, verify=False)
    token = ret.json()['return'][0]['token']

    url = 'https://192.168.10.110:8001/'
    headers = {
        'Accept': 'application/json',
        'X-Auth-Token': token,
    }

    # 更新配置文件中的ip
    cmd = "/usr/bin/salt 'saltServer' cmd.run 'sed -i \"s/{old_ip}/{new_ip}/g\" /data/salt/leida_nginx/dev/*'".format(
        old_ip=old_ip,
        new_ip=new_ip
    )
    print('cmd -->', cmd)
    post_data = {
        'client': 'local',
        'tgt': 'saltServer',
        'fun': 'cmd.run',
        'arg': cmd,
    }
    ret = requests.post(url, post_data, headers=headers, verify=False)


    # 下发配置文件
    cmd = "/usr/bin/salt 'saltServer' cmd.run 'salt 'zhuanfaji' state.sls zhugeleida_dev'"
    print('cmd -->', cmd)
    post_data = {
        'client': 'local',
        'tgt': 'saltServer',
        'fun': 'cmd.run',
        'arg': cmd,
    }
    ret = requests.post(url, post_data, headers=headers, verify=False)

    # 重启nginx
    cmd = "/usr/bin/salt 'zhuanfaji' cmd.run '/data/application/nginx-1.10.3/sbin/nginx -s reload'"
    print('cmd -->', cmd)
    post_data = {
        'client': 'local',
        'tgt': 'saltServer',
        'fun': 'cmd.run',
        'arg': cmd,
    }
    ret = requests.post(url, post_data, headers=headers, verify=False)

    print(ret.text)
