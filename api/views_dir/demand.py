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
from django.db.models import Q, Count

from publicFunc.workWeixin import workWeixinApi


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def demand(request):
    user_id = request.GET.get('user_id')
    response = Response.ResponseObj()
    if request.method == "GET":
        print('request.GET -->', request.GET)
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            developer_id = request.GET.get('developer_id')
            demandUser = request.GET.get('demandUser')    # 提需求人筛选
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            status = request.GET.get('status')
            role_id = forms_obj.cleaned_data['role_id']
            company_id = forms_obj.cleaned_data['company_id']
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
                'status': '',
                'urgency_level': '',
                'project_id': ''
            }
            q = conditionCom(request, field_dict)
            if developer_id:
                demand_id_list = [i['demand_id'] for i in models.demand_to_userprofile.objects.filter(developer_id=developer_id).values('demand_id')]
                q.add(Q(**{'id__in': demand_id_list}), Q.AND)
            if demandUser:
                q.add(Q(**{'oper_user_id':demandUser}), Q.AND)

            if role_id == 2:    # 管理员角色只能看自己公司的
                q.add(Q(**{'project__company_id': company_id}), Q.AND)
            elif role_id == 3:  # 项目负责人/产品经理角色
                project_objs = models.project.objects.all()
                project_id_list = []
                for project_obj in project_objs:
                    if project_obj.principal.filter(id=user_id):    # 如果该项目的负责人有当前人
                        project_id_list.append(project_obj.id)
                q.add(Q(**{'project_id__in': project_id_list}), Q.AND)

            elif role_id == 4:  # 开发角色
                demand_id_list = [i['demand_id'] for i in models.demand_to_userprofile.objects.filter(developer_id=user_id).values('demand_id')]
                print('demand_id_list -->', demand_id_list)
                q.add(Q(**{'id__in': demand_id_list}), Q.AND)

            print('q -->', q)
            if status:
                objs = models.demand.objects.select_related('action', 'project').filter(q).order_by(order)
            else:
                objs = models.demand.objects.select_related('action', 'project', 'project__company').filter(q).exclude(status=11).order_by(order)

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

                developer = ",".join([i['developer__username'] for i in obj.demand_to_userprofile_set.values('developer__username')])
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
                    'developer': developer,
                    'status_text': obj.get_status_display(),
                    'urgency_level': obj.urgency_level,
                    'urgency_level_text': obj.get_urgency_level_display(),
                    'project__name_action__name': "%s - %s" % (obj.project.name, obj.action.name),
                    'create_date': obj.create_date.strftime('%y-%m-%d %H:%M'),
                    'complete_date': complete_date,
                    'oper_user__username': oper_user_username,
                })
            demand_user_list = []
            userObjs = models.userprofile.objects.filter(status=1)
            for i in userObjs:
                demand_user_list.append({
                    'user_id':i.id,
                    'user_name':i.username,
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'status_choices': models.demand.status_choices,
                'urgency_level_choices': models.demand.urgency_level_choices,
                'demand_user':demand_user_list,

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
    work_weixin_api_obj = workWeixinApi.WorkWeixinApi()
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

                project_id = forms_obj.cleaned_data.get('project_id')
                project_obj = models.project.objects.get(id=project_id)

                print(project_obj.principal.all().values('userid'))
                userID = "|".join([i['userid'] for i in project_obj.principal.values('userid')])
                msg = "您的项目 {project_name} 有新的需求等待审核，请及时处理".format(
                    project_name=project_obj.name
                )
                work_weixin_api_obj.message_send(userID, msg)

                obj = models.progress.objects.create(
                    demand=obj,
                    description="创建需求",
                    create_user_id=forms_obj.cleaned_data.get('oper_user_id')
                )
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
            objs = models.demand.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                if obj.status == 1:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 300
                    response.msg = "该需求不能删除，如需删除请联系项目负责人关闭需求"
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

                    project_obj = models.project.objects.get(id=project_id)
                    userID = "|".join([i['userid'] for i in project_obj.principal.values('userid')])
                    msg = "您的项目 {project_name} 有需求被修改，等待审核中，请及时处理".format(
                        project_name=project_obj.name
                    )
                    work_weixin_api_obj.message_send(userID, msg)

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
                objs = models.demand.objects.select_related('project').filter(id=o_id)
                if objs:
                    obj = objs[0]
                    obj.status = 2
                    obj.save()

                    query = []
                    for developer in json.loads(developerList):
                        query.append(
                            models.demand_to_userprofile(developer_id=developer, demand_id=obj.id)
                        )
                    models.demand_to_userprofile.objects.bulk_create(query)

                    user_obj = models.userprofile.objects.filter(id__in=json.loads(developerList))
                    userID = "|".join([i['userid'] for i in user_obj.values('userid')])
                    msg = "项目 {project_name} 有新的需求等待开发，请及时处理".format(
                        project_name=obj.project.name
                    )
                    work_weixin_api_obj.message_send(userID, msg)

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

            userID = objs[0].oper_user.userid
            msg = "您提交的需求 {id}-{name} 开发工程师已经估算开发时间，预计开发完成时间: {new_date}".format(
                id=objs[0].id,
                name=objs[0].name,
                new_date=complete_date
            )
            print('userID -->', userID)
            work_weixin_api_obj.message_send(userID, msg)

            response.code = 200
            response.msg = "预计开发时间设置成功"
            # 开发人员修改预计完成时间

        # 延迟开发完成时间
        elif oper_type == "yanchi_complete_date":
            complete_date = request.POST.get('complete_date')
            remark = request.POST.get('remark')
            oper_user_id = request.GET.get('user_id')
            objs = models.demand.objects.select_related('oper_user').filter(id=o_id)
            old_complete_date = objs[0].complete_date
            objs.update(complete_date=complete_date)

            models.progress.objects.create(
                demand=objs[0],
                remark=remark,
                description="延迟预计开发时间，原预计开发时间: {old_date}，新预计开发时间: {complete_date}".format(
                    old_date=old_complete_date,
                    complete_date=complete_date
                ),
                create_user_id=oper_user_id
            )

            userID = objs[0].oper_user.userid
            msg = "您提交的需求 {id}-{name} 需要延期处理，原预计开发完成时间: {old_date}，新预计开发完成时间: {new_date}".format(
                id=objs[0].id,
                name=objs[0].name,
                old_date=old_complete_date,
                new_date=complete_date
            )
            print('userID -->', userID)
            work_weixin_api_obj.message_send(userID, msg)

            response.code = 200
            response.msg = "延迟开发时间设置成功"

        # 开发人员开发完成后提交开发需求
        elif oper_type == "tijiao_ceshi":
            remark = request.POST.get('remark')
            oper_user_id = request.GET.get('user_id')
            objs = models.demand.objects.select_related('oper_user').filter(id=o_id)
            objs.update(
                status=4
            )

            models.progress.objects.create(
                demand=objs[0],
                description="开发完成，提交进行测试",
                create_user_id=oper_user_id,
                remark=remark
            )

            userID = objs[0].oper_user.userid
            msg = "您提交的需求 {id}-{name} 已开发完成，请进行测试".format(
                id=objs[0].id,
                name=objs[0].name
            )
            work_weixin_api_obj.message_send(userID, msg)
            response.code = 200
            response.msg = "提交成功"

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

            project_obj = models.project.objects.get(id=objs[0].project_id)
            userID = "|".join([i['userid'] for i in project_obj.principal.values('userid')])

            msg = "需求 {id}-{name} 已测试完成，可进行上线操作，请及时处理".format(
                id=objs[0].id,
                name=objs[0].name
            )
            work_weixin_api_obj.message_send(userID, msg)

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
            userObjs = models.demand_to_userprofile.objects.filter(demand_id=o_id)
            otherData = []
            for userObj in userObjs:
                otherData.append(userObj.developer.username)
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

            response.data = {
                'result_data': result_data,
                'kaifa_username': otherData
                             }
            response.msg = "查询成功"
            response.code = 200

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)

# 定时刷新 判断需求创建时间 推送企业微信 及时完成开发
def pushMessageToWeChat(request):
    work_weixin_api_obj = workWeixinApi.WorkWeixinApi()
    response = Response.ResponseObj()
    userIdList = []
    mS = time.strftime('%M')  # 当前分钟
    now_datetime = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime(
        '%Y-%m-%d %H:%M:%S')  # 条件创建时间 要大于一小时

    q = Q()
    q.add(Q(create_date__lte=now_datetime), Q.AND)
    # q.add(Q(status=1) | Q(status=2) | Q(status=3), Q.AND)
    q.add(Q(status=1) | Q(status=2), Q.AND)
    objs = models.demand.objects.filter(q)  # 获取所有 需求
    for obj in objs:
        # if mS == datetime.date.strftime(obj.create_date, '%M'): # 当前分钟数 等于 创建分钟数 相当于 每隔一小时可进入一次
        if obj.status == 1:  # 待审核 提醒
            userID = 'zhangcong'
            msg = '有待审核需求, 请尽快审核！'
            work_weixin_api_obj.message_send(userID, msg)
        elif obj.status == 2:  # 待评估 提醒
            # print('obj.id=============> ', obj.id)
            # userObjs = models.userprofile.objects.project_set()
            userObjs = obj.project.developer.all()  # 获取该需求所有开发人
            for userObj in userObjs:
                userIdList.append(userObj.userid)
    for userID in set(userIdList):
        msg = '有待评估需求, 请尽快查看、开发！'
        work_weixin_api_obj.message_send(userID, msg)
    response.code = 200
    response.msg = '查询成功'
    return JsonResponse(response.__dict__)