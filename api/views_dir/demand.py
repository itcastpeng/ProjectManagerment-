from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from api.forms.demand import AddForm, UpdateForm, SelectForm
import json
from django.db.models import Q


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def demand(request):
    user_id = request.GET.get('user_id')
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            role_id = forms_obj.cleaned_data['role_id']
            company_id = forms_obj.cleaned_data['company_id']
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
            }
            q = conditionCom(request, field_dict)

            if role_id == 2:  # 管理员角色
                q.add(Q(**{'project__company_id': company_id}), Q.AND)

            elif role_id in [3, 4]:  # 3 -->项目负责人/产品经理  4 --> 开发负责人
                project_objs = models.project.objects.all()
                project_id_list = []
                for project_obj in project_objs:
                    if role_id == 3:
                        if project_obj.principal.filter(id=user_id):    # 如果该项目的负责人有当前人
                            project_id_list.append(project_obj.id)
                    elif role_id == 4:
                        if project_obj.developer.filter(id=user_id):    # 如果该项目的开发人有当前人
                            project_id_list.append(project_obj.id)
                q.add(Q(**{'project_id__in': project_id_list}), Q.AND)

            print('q -->', q)
            objs = models.demand.objects.select_related('action', 'project').filter(q).order_by(order)
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
                complete_date = ''
                if obj.complete_date:
                    complete_date = obj.create_date.strftime('%y-%m-%d %H:%M')
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'remark': obj.remark,
                    'action__name': obj.action.name,
                    'action_id': obj.action_id,
                    'project_id': obj.project_id,
                    'status': obj.status,
                    'status_text': obj.get_status_display(),
                    'urgency_level': obj.urgency_level,
                    'urgency_level_text': obj.get_urgency_level_display(),
                    'project_name': obj.project.name,
                    'project__name_action__name': "%s - %s" % (obj.project.name, obj.action.name),
                    'create_date': obj.create_date.strftime('%y-%m-%d %H:%M'),
                    'complete_date': complete_date,
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
def demand_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'oper_user_id': request.GET.get('user_id'),
                'project_id': request.POST.get('project_id'),
                'action_id': request.POST.get('action_id'),
                'name': request.POST.get('name'),
                'remark': request.POST.get('remark'),
                'complete_date': request.POST.get('complete_date'),
                'img_list': request.POST.get('img_list'),
                'urgency_level': request.POST.get('urgency_level')
            }
            print('form_data -->', form_data)
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                models.demand.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        # elif oper_type == "delete":
        #     # 删除 ID
        #     # 如果需求进展中有数据，则不允许删除
        #     progress_objs = models.progress.objects.filter(demand_id=o_id)
        #     if not progress_objs:
        #         objs = models.demand.objects.filter(id=o_id)
        #         if objs:
        #             objs.delete()
        #             response.code = 200
        #             response.msg = "删除成功"
        #         else:
        #             response.code = 302
        #             response.msg = '删除ID不存在'
        #     else:
        #         response.code = 304
        #         response.msg = '含有子级数据,请先删除或转移子级数据'
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
