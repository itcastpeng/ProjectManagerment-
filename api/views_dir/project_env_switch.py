from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from api.forms.project import AddForm, UpdateForm, SelectForm
import json
from django.db.models import Q
import requests

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def project_env_switch(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            role_id = forms_obj.cleaned_data['role_id']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            user_id = request.GET.get('user_id')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'company_id': '',
                'oper_user__username': '__contains',
            }
            if role_id == 2:  # 管理员角色
                field_dict['company_id'] = ''

            q = conditionCom(request, field_dict)
            print('q -->', q)
            q.add(Q(**{'is_switch': True}), Q.AND)

            #  将查询出来的数据 加入列表
            print('q -->', q)
            objs = models.project.objects.select_related('company').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                #  如果有oper_user字段 等于本身名字
                if obj.oper_user:
                    oper_user_username = obj.oper_user.username
                else:
                    oper_user_username = ''
                # print('oper_user_username -->', oper_user_username)

                # 项目负责人列表
                principal_objs = obj.principal.values('username', 'id')
                principal_list = [i['username'] for i in principal_objs]
                principal_id_list = [i['id'] for i in principal_objs]

                # 开发负责人列表
                developer_objs = obj.developer.values('username', 'id')
                developer_list = [i['username'] for i in developer_objs]
                developer_id_list = [i['id'] for i in developer_objs]

                # print('principal_list -->', principal_list)
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'principal_list': ','.join(principal_list),
                    'principal_id_list': principal_id_list,
                    'developer_list': ','.join(developer_list),
                    'developer_id_list': developer_id_list,
                    'company_name': obj.company.name,
                    'company_id': obj.company_id,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': obj.status,
                    'get_status_display': obj.get_status_display(),
                    'oper_user__username': oper_user_username,
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def project_env_switch_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "switch_status":    # 切换正式和灰度状态

            objs = models.project.objects.filter(id=o_id, is_switch=True)
            if objs:
                obj = objs[0]
                if obj.id == 1:
                    if obj.status == 1:
                        arg = 'zhugeleida_dev'
                        status = 2
                    else:
                        arg = 'zhugeleida_prod'
                        status = 1
                    switch_zhugeleida(arg)
                    obj.status = status
                    obj.save()

                response.code = 200
                response.msg = "添加成功"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 诸葛雷达切换正式和灰度环境
def switch_zhugeleida(arg):
    # 先登录获取token
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
    post_data = {
        'client': 'local',
        'tgt': 'zhuanfaji',
        'fun': 'state.sls',
        'arg': arg,
    }
    ret = requests.post(url, post_data, headers=headers, verify=False)