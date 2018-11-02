from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.configurationManagementHOST import AddForm, UpdateForm, SelectForm
from api.views_dir.permissions import init_data
import json
import time
import datetime
from django.db.models import Q

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def configurationHost(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            # order = request.GET.get('order', '-create_date')
            taskName = request.GET.get('taskName')
            # print('order-------> ',order)
            field_dict = {
                'id': '',
                'hostName': '__contains',
                'hostUrl': '',
                'userProfile_id': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.configurationManagementHOST.objects.filter(q)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'name': obj.hostName,
                    'url':obj.hostUrl,
                    'username': obj.userProfile.username,
                    'user_id': obj.userProfile.id,
                    'describe_id': obj.describe,
                    'describe': obj.get_describe_display(),
                    'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),

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
def configurationHostOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    form_data = {
        'o_id':o_id,
        'user_id': request.GET.get('user_id'),                   # 操作人
        'hostName': request.POST.get('hostName'),                   # 操作人
        'hostUrl': request.POST.get('hostUrl'),                  # 分组名称
        'describe': request.POST.get('describe')
    }
    print('form_data========>', form_data)
    userObjs = models.configurationManagementHOST.objects
    if request.method == "POST":
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                now_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if userObjs:
                    formResult = forms_obj.cleaned_data
                    userObjs.create(
                        hostName=formResult.get('hostName'),
                        hostUrl=formResult.get('hostUrl'),
                        userProfile_id=form_data.get('user_id'),
                        create_date=now_date,
                        describe=formResult.get('describe'),
                    )
                    response.code = 200
                    response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update":
            # 获取需要修改的信息
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                oidObjs = userObjs.filter(id=o_id)
                if oidObjs:
                    formResult = forms_obj.cleaned_data
                    userObjs.filter(id=o_id).update(
                        hostName=formResult.get('hostName'),
                        hostUrl=formResult.get('hostUrl'),
                        userProfile_id=form_data.get('user_id'),
                        describe=formResult.get('describe'),
                    )
                    response.code = 200
                    response.msg = '修改成功'
                else:
                    response.code = 402
                    response.msg = '修改ID错误'
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            oidObjs = userObjs.filter(id=o_id)
            if oidObjs:
                oidObjs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
    else:
        if oper_type == 'miaoShuResult':
            objs = models.configurationManagementHOST.status_choices
            otherData = []
            for obj in objs:
                otherData.append({
                    'id': obj[0],
                    'status':obj[1]
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData':otherData}
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
