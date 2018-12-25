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
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                new_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                new_ip = request.META['REMOTE_ADDR']

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
