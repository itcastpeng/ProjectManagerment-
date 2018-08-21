from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import time
import datetime
from publicFunc.condition_com import conditionCom
from api.forms.demand import AddForm, UpdateForm, SelectForm, ShenHeForm
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
                'status': '',
                'urgency_level': ''
            }
            q = conditionCom(request, field_dict)

            if role_id !=1:  # 非超级管理员角色都只能看自己公司的
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
                    complete_date = obj.complete_date.strftime('%y-%m-%d %H:%M')
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'remark': obj.remark,
                    'action__name': obj.action.name,
                    'action_id': obj.action_id,
                    'project_id': obj.project_id,
                    'project_name': obj.project.name,
                    'status': obj.status,
                    'img_list': obj.img_list,
                    'status_text': obj.get_status_display(),
                    'urgency_level': obj.urgency_level,
                    'urgency_level_text': obj.get_urgency_level_display(),
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
                'status_choices': models.demand.status_choices,
                'urgency_level_choices': models.demand.urgency_level_choices
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
                # 'complete_date': request.POST.get('complete_date'),
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
                obj = models.demand.objects.create(**forms_obj.cleaned_data)

                models.progress.objects.create(
                    demand=obj,
                    description="创建需求",
                    create_user_id=forms_obj.cleaned_data.get('oper_user_id')
                )
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
            objs = models.demand.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                if obj.status == 1:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 300
                    response.msg = "该需求已经不能删除，如需删除请联系项目负责人关闭需求"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'oper_user_id': request.GET.get('user_id'),
                'project_id': request.POST.get('project_id'),
                'action_id': request.POST.get('action_id'),
                'name': request.POST.get('name'),
                'remark': request.POST.get('remark'),
                'img_list': request.POST.get('img_list'),
                'urgency_level': request.POST.get('urgency_level')
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                project_id = forms_obj.cleaned_data['project_id']
                action_id = forms_obj.cleaned_data['action_id']
                remark = forms_obj.cleaned_data['remark']
                img_list = forms_obj.cleaned_data['img_list']
                urgency_level = forms_obj.cleaned_data['urgency_level']
                #  查询数据库  用户id
                objs = models.demand.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name,
                        project_id=project_id,
                        action_id=action_id,
                        remark=remark,
                        img_list=img_list,
                        urgency_level=urgency_level
                    )

                    models.progress.objects.create(
                        demand=objs[0],
                        description="修改需求",
                        create_user_id=forms_obj.cleaned_data.get('oper_user_id')
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

        # 项目负责人审核需求，分配开发人员
        elif oper_type == "shenhe":
            form_data = {
                'o_id': o_id,
                'oper_user_id': request.GET.get('user_id'),
                'developerList': request.POST.get('developerList'),
                'remark': request.POST.get('remark'),
            }
            print('form_data -->', form_data)
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = ShenHeForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                #  添加数据库
                print('forms_obj.cleaned_data-->', forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data.get('o_id')
                oper_user_id = forms_obj.cleaned_data.get('oper_user_id')
                developerList = forms_obj.cleaned_data.get('developerList')
                remark = forms_obj.cleaned_data.get('remark')
                objs = models.demand.objects.filter(id=o_id)
                if objs:
                    obj = objs[0]
                    obj.status = 2
                    obj.save()
                    obj.developer = json.loads(developerList)

                    models.progress.objects.create(
                        demand=obj,
                        remark=remark,
                        description="审核需求,分配开发需求",
                        create_user_id=oper_user_id
                    )

                    response.code = 200
                    response.msg = "审核成功"
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        # 开发人员修改预计完成时间
        elif oper_type == "update_complete_date":
            complete_date = request.POST.get('complete_date')
            oper_user_id = request.GET.get('user_id')
            objs = models.demand.objects.filter(id=o_id)
            objs.update(
                complete_date=complete_date,
                status=3
            )

            models.progress.objects.create(
                demand=objs[0],
                description="设置预计开发时间，预计 {complete_date} 开发完成".format(complete_date=complete_date),
                create_user_id=oper_user_id
            )

            response.code = 200
            response.msg = "预计开发时间设置成功"
            # 开发人员修改预计完成时间

        # 延迟开发完成时间
        elif oper_type == "yanchi_complete_date":
            complete_date = request.POST.get('complete_date')
            remark = request.POST.get('remark')
            oper_user_id = request.GET.get('user_id')
            objs = models.demand.objects.filter(id=o_id)
            objs.update(complete_date=complete_date)

            models.progress.objects.create(
                demand=objs[0],
                remark=remark,
                description="延迟预计开发时间，预计 {complete_date} 开发完成".format(complete_date=complete_date),
                create_user_id=oper_user_id
            )

            response.code = 200
            response.msg = "延迟开发时间设置成功"

        # 开发人员开发完成后提交开发需求
        elif oper_type == "tijiao_ceshi":
            remark = request.POST.get('remark')
            oper_user_id = request.GET.get('user_id')
            objs = models.demand.objects.filter(id=o_id)
            objs.update(
                status=4
            )

            models.progress.objects.create(
                demand=objs[0],
                description="开发完成，提交进行测试",
                create_user_id=oper_user_id,
                remark=remark
            )

            response.code = 200
            response.msg = "预计开发时间设置成功"

        # 测试通过，需求交付
        elif oper_type == "jiaofu":
            remark = request.POST.get('remark')
            oper_user_id = request.GET.get('user_id')
            objs = models.demand.objects.filter(id=o_id)
            objs.update(
                status=6
            )

            models.progress.objects.create(
                demand=objs[0],
                description="测试完成，需求交付完成",
                create_user_id=oper_user_id,
                remark=remark
            )

            response.code = 200
            response.msg = "预计开发时间设置成功"

        # 关闭需求
        elif oper_type == "close":
            oper_user_id = request.GET.get('user_id')
            remark = request.POST.get('remark')
            objs = models.demand.objects.filter(id=o_id)
            if objs:
                objs.update(
                    status=11
                )
                print('remark -->', remark)
                print('oper_user_id -->', oper_user_id)

                models.progress.objects.create(
                    demand=objs[0],
                    remark=remark,
                    description="关闭需求",
                    create_user_id=oper_user_id
                )

                response.code = 200
                response.msg = "需求关闭成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
    else:
        if oper_type == "detail":
            result_data = []
            objs = models.progress.objects.select_related('create_user').filter(demand_id=o_id)
            for obj in objs:
                result_data.append({
                    'description': obj.description,
                    'remark': obj.remark,
                    'img_list': obj.img_list,
                    'create_date': obj.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'create_user__username': obj.create_user.username,
                    'create_user_id': obj.create_user_id,
                })
            response.data = result_data
            response.msg = "查询成功"
            response.code = 200
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
