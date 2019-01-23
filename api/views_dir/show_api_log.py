from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from api.forms.showApiLog import ShowLogForm
import json
from django.db.models import Q
import requests

from publicFunc.saltOper import SaltOper


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def show_api_log(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        objs = models.showApiLog.objects.all()

        print('objs -->', objs)

        ret_data = []
        for obj in objs:
            ret_data.append({
                "id": obj.id,
                "name": obj.name
            })
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
        }

    return JsonResponse(response.__dict__)


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def show_api_log_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "GET":
        if oper_type == "showLog":
            # o_id 要获取的项目id
            lineNum = request.GET.get('lineNum')        # 表示要获取从多少行开始的数据，如果该值为0，则表示首次获取
            filterKeyWorld = request.GET.get('filterKeyWorld')     # 匹配过滤条件
            form_data = {
                "lineNum": lineNum,
                "filterKeyWorld": filterKeyWorld
            }

            # form 验证
            forms_obj = ShowLogForm(form_data)
            if forms_obj.is_valid():
                lineNum = forms_obj.cleaned_data.get('lineNum')
                filterKeyWorld = forms_obj.cleaned_data.get('filterKeyWorld')

                objs = models.showApiLog.objects.filter(id=o_id)
                if objs:

                    obj = objs[0]
                    tgt = obj.tgt
                    logPath = obj.logPath
                    salt_api_showApiLog(lineNum, tgt, logPath, filterKeyWorld)

                    lineNum += 10
                    response.data = {
                        'lineNum': lineNum,
                        'logData': ['{lineNum}fdsafdafdas'.format(lineNum=lineNum)]
                    }
                    response.code = 200
                    response.msg = "查询成功"

                else:
                    response.code = 302
                    response.msg = "查询ID不存在"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)



# # 通过salt获取api日志
def salt_api_showApiLog(lineNum, tgt, logPath, filterKeyWorld):
    # 先登录获取token
    saltObj = SaltOper()

    print(lineNum, tgt, logPath, filterKeyWorld)
    cmd = "cat {logPath} | wc -l".format(logPath=logPath)

    result = saltObj.cmdRun(tgt, cmd)
    lastLinuNum = result['return'][0][tgt]
    # print('lastLinuNum -->', lastLinuNum)

    result_data = {
        'lineNum': lastLinuNum,
        'logData': []
    }
    if lineNum == 0:        # 首次获取
        return result_data
    else:
        if lastLinuNum - lineNum > 100:     # 如果新日志大于100条，则只取100条
            result_data['lineNum'] = lineNum + 100
        else:
            result_data['lineNum'] = lastLinuNum

        cmd = "sed -n '{startLineNum},{stopLineNum}p' {logPath}".format(
            startLineNum=lineNum,
            stopLineNum=result_data['lineNum'],
            logPath=logPath
        )
        result = saltObj.cmdRun(tgt, cmd)
        print('result -->', result)
        return result_data


# # 通过 salt 执行代码上线
# def salt_api_zhugeleida_code_online(pid, code_env):
#     # 先登录获取token
#     url = 'https://192.168.10.110:8001/login'
#     headers = {
#         'Accept': 'application/json',
#     }
#     post_data = {'username': 'saltapi', 'password': 'saltapi@2018', 'eauth': 'pam'}
#
#     ret = requests.post(url, post_data, headers=headers, verify=False)
#     print('login_ret  -->', ret.json())
#     token = ret.json()['return'][0]['token']
#
#     url = 'https://192.168.10.110:8001/'
#     headers = {
#         'Accept': 'application/json',
#         'X-Auth-Token': token,
#     }
#
#     print(pid, type(pid), code_env, type(code_env))
#     if pid == 1:    # 雷达项目
#         if code_env == 1:  # 雷达AI代码上线（前端）
#             post_data = {
#                 'client': 'local_async',
#                 'tgt': 'huidu-web-03',
#                 'fun': 'state.sls',
#                 'arg': 'zhugeleida_code_online_zhugeLeida',
#             }
#         elif code_env == 2:     # 雷达后台代码上线（前端）
#             post_data = {
#                 'client': 'local_async',
#                 'tgt': 'huidu-web-03',
#                 'fun': 'state.sls',
#                 'arg': 'zhugeleida_code_online_zhugeleidaAdmin',
#             }
#         elif code_env == 3:  # 雷达API代码上线（后端）
#             post_data = {
#                 'client': 'local_async',
#                 'tgt': 'huidu-web-03',
#                 'fun': 'state.sls',
#                 'arg': 'zhugeleida_code_online_zhugeleidaApi',
#             }
#
#     print('post_data -->', post_data)
#     ret = requests.post(url, post_data, headers=headers, verify=False)
#     print('zhixing  -->', ret.json())
#     # {'return': [{'minions': ['huidu-web-03'], 'jid': '20180904143828065729'}]}
#     return ret.json()
#
#
# # 通过jobid查询任务状态
# def salt_api_search_jobid(jobid):
#     # 先登录获取token
#     url = 'https://192.168.10.110:8001/login'
#     headers = {
#         'Accept': 'application/json',
#     }
#     post_data = {'username': 'saltapi', 'password': 'saltapi@2018', 'eauth': 'pam'}
#
#     ret = requests.post(url, post_data, headers=headers, verify=False)
#     print('login_ret  -->', ret.json())
#     token = ret.json()['return'][0]['token']
#
#     url = 'https://192.168.10.110:8001/'
#     print('url -->', url)
#     headers = {
#         'Accept': 'application/json',
#         'X-Auth-Token': token,
#     }
#
#     # post_data = {
#     #     'client': 'local',
#     #     'tgt': 'huidu-web-03',
#     #     'fun': 'saltutil.find_job',
#     #     'arg': jobid
#     # }
#
#     post_data = {
#         'client': 'runner',
#         'tgt': 'huidu-web-03',
#         'fun': 'jobs.lookup_jid',
#         'jid': jobid
#     }
#
#     ret = requests.post(url, data=post_data, headers=headers, verify=False)
#     print(ret.text)
#     # print('zhixing  -->', ret.json())
#     # {'return': [{'minions': ['huidu-web-03'], 'jid': '20180904143828065729'}]}
#     return ret.json()