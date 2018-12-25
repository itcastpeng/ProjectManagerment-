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


# cerf  token验证 用户展示模块
@csrf_exempt
def switch_nginx_huidu_ip(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        print('request.META -->', request.META)

        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        response.code = 200
        response.data = {
            'ip': ip
        }

    return JsonResponse(response.__dict__)


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def switch_nginx_huidu_ip_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'permissionsList': request.POST.get('permissionsList'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                # print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                print({
                    'name': forms_obj.cleaned_data.get('name'),
                    'oper_user_id': forms_obj.cleaned_data.get('oper_user_id'),
                })
                obj = models.role.objects.create(**{
                    'name': forms_obj.cleaned_data.get('name'),
                    'oper_user_id': forms_obj.cleaned_data.get('oper_user_id'),
                })

                permissionsList = forms_obj.cleaned_data.get('permissionsList')
                print('permissionsList -->', permissionsList)
                obj.permissions = permissionsList
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            objs = models.role.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                if obj.userprofile_set.all().count() > 0:
                    response.code = 304
                    response.msg = '含有子级数据,请先删除或转移子级数据'
                else:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'permissionsList': request.POST.get('permissionsList'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                permissionsList = forms_obj.cleaned_data['permissionsList']
                #  查询数据库  用户id
                objs = models.role.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name
                    )

                    objs[0].permissions = permissionsList

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 获取角色对应的权限
        if oper_type == "get_rules":
            objs = models.role.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                rules_list = [i['name'] for i in obj.permissions.values('name')]
                print('dataList -->', rules_list)
                response.data = {
                    'rules_list': rules_list
                }

                response.code = 200
                response.msg = "查询成功"
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
