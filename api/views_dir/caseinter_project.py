from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.caseinter_project import AddForm, UpdateForm, SelectForm
import json


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def caseinter_project(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            user_id = request.GET.get('user_id')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
            }

            q = conditionCom(request, field_dict)

            #  将查询出来的数据 加入列表
            print('q -->', q)
            objs = models.caseInterProject.objects.filter(q).order_by(order)
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
                # principal_objs = obj.principal.values('username', 'id')
                # principal_list = [i['username'] for i in principal_objs]
                # principal_id_list = [i['id'] for i in principal_objs]

                # 开发负责人列表
                developer_objs = obj.developer.values('username', 'id')
                developer_list = [i['username'] for i in developer_objs]
                developer_id_list = [i['id'] for i in developer_objs]

                # print('principal_list -->', principal_list)
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    # 'principal_list': ','.join(principal_list),
                    # 'principal_id_list': principal_id_list,
                    'developer_list': ','.join(developer_list),
                    'developer_id_list': developer_id_list,
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
def caseinter_project_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        if oper_type == "add":
            form_data = {
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),                       # 项目名称
                # 'principalList': request.POST.get('principalList'),     # 负责人
                'developerList': request.POST.get('developerList'),     # 开发人员
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                obj = caseInterProject_obj = models.caseInterProject.objects.create(
                    name=forms_obj.cleaned_data['name'],
                    oper_user_id=forms_obj.cleaned_data['oper_user_id']
                )
                # caseInterProject_obj.principal = json.loads(forms_obj.cleaned_data['principalList'])
                caseInterProject_obj.developer = json.loads(forms_obj.cleaned_data['developerList'])
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            host_obj = models.configurationManagementHOST.objects.filter(id=o_id)
            if not host_obj:
                group_obj = models.caseInterfaceGrouping.objects.filter(id=o_id)
                if not group_obj:
                    objs = models.caseInterProject.objects.filter(id=o_id)
                    if objs:
                        objs.delete()
                        response.code = 200
                        response.msg = "删除成功"
                    else:
                        response.code = 302
                        response.msg = '删除ID不存在'
                else:
                    response.code = 301
                    response.msg = '含有子级, 请先移除'
            else:
                response.code = 301
                response.msg = '含有子级, 请先移除'

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                # 'principalList': request.POST.get('principalList'),
                'developerList': request.POST.get('developerList'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']

                #  查询数据库
                objs = models.caseInterProject.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(name=name)
                    # objs[0].principal = json.loads(forms_obj.cleaned_data['principalList'])
                    objs[0].developer = json.loads(forms_obj.cleaned_data['developerList'])

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        if oper_type =='getTaskName':
            objs = models.caseInterProject.objects.filter(developer=user_id)
            otherData = []
            for obj in objs:
                otherData.append({
                    'id': obj.id,
                    'name': obj.name
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData': otherData}

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
