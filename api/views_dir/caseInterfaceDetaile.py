from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.caseInterfaceDetaile import AddForm, UpdateForm, SelectForm
from api.views_dir.permissions import init_data
import json
import time
import datetime


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def testCaseDetaileShow(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            # order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'talkProject': '__contains',
                'parensGroupName': '',
                'operUser': '__contains',
                'groupName': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.caseInterfaceGrouping.objects.filter(q)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                parensGroupName = ''
                parensGroupName_id = ''
                if obj.parensGroupName:
                    parensGroupName = obj.parensGroupName.groupName
                    parensGroupName_id = obj.parensGroupName.id
                talkName = ''
                talkProject_id = ''
                if obj.talkProject:
                    talkName = obj.talkProject.name
                    talkProject_id = obj.talkProject.id
                ret_data.append({
                    'id': obj.id,
                    'groupName': obj.groupName,
                    'parensGroupName_id':parensGroupName_id,
                    'parensGroupName': parensGroupName,
                    'operUser': obj.operUser.username,
                    'operUser_id':obj.operUser.id,
                    'talkProject_id':talkProject_id,
                    'talkProject': talkName
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
def testCaseDetaileOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    form_data = {
        'o_id':o_id,
        'url': request.POST.get('url'),                   # url
        'user_id': request.POST.get('user_id'),                   # 操作人
        'ownershipGroup_id': request.POST.get('ownershipGroup_id'),     # 分组名称
    }
    detaileObjs = models.caseInterfaceDetaile.objects
    print('form_data========>', form_data)
    if request.method == "POST":
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                formResult = forms_obj.cleaned_data
                detaileObjs.create(
                    url=formResult.get('url'),
                    ownershipGroup_id=formResult.get('ownershipGroup_id')
                )
                response.code = 200
                response.msg = '添加成功'

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
                print("验证通过")
                #  查询数据库  用户id
                formResult = forms_obj.cleaned_data
                detaileObjs.filter(id=o_id).update(
                    url=formResult.get('url'),
                    ownershipGroup_id=formResult.get('ownershipGroup_id')
                )
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        if oper_type == "delete":
            # 删除 ID
            objs = models.caseInterfaceDetaile.objects
            oidObjs = objs.filter(id=o_id)
            if oidObjs:
                    oidObjs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)