from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from api.forms.action import AddForm, UpdateForm, SelectForm
import json
from django.db.models import Q


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def action(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            company_id = forms_obj.cleaned_data['company_id']
            role_id = forms_obj.cleaned_data['role_id']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
                'project_id': '',
            }

            q = conditionCom(request, field_dict)
            if role_id == 2:  # 管理员角色
                q.add(Q(**{'project__company_id': company_id}), Q.AND)

            print('q -->', q)
            objs = models.action.objects.select_related('project').filter(q).order_by(order)
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
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'project__name': obj.project.name,
                    'project_id': obj.project_id,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
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
def action_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'project_id': request.POST.get('project_id'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                models.action.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            # 如果产品需求表中有数据，则不允许删除
            demand_objs = models.demand.objects.filter(action_id=o_id)
            if not demand_objs:
                objs = models.action.objects.filter(id=o_id)
                if objs:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 302
                    response.msg = '删除ID不存在'
            else:
                response.code = 304
                response.msg = '含有子级数据,请先删除或转移子级数据'
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'project_id': request.POST.get('project_id'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                project_id = forms_obj.cleaned_data['project_id']
                #  查询数据库  用户id
                objs = models.action.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name,
                        project_id=project_id
                    )

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
        elif oper_type == "update_status":
            status = request.POST.get('status')
            print('status -->', status)
            models.userprofile.objects.filter(id=o_id).update(status=status)
            response.code = 200
            response.msg = "状态修改成功"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
