from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.caseinter_project import AddForm, UpdateForm, SelectForm, DeleteForm
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

                # 前端开发负责人列表
                front_developer_objs = obj.front_developer.values('username', 'id')
                front_developer_list = [i['username'] for i in front_developer_objs]
                front_developer_id_list = [i['id'] for i in front_developer_objs]

                # 后端开发负责人列表
                back_developer_objs = obj.back_developer.values('username', 'id')
                back_developer_list = [i['username'] for i in back_developer_objs]
                back_developer_id_list = [i['id'] for i in back_developer_objs]

                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,

                    'language_type_id': obj.language_type,                          # 语言类型 区分请求结果
                    'language_type': obj.get_language_type_display(),               # 语言类型 区分请求结果

                    'front_developer_id_list': front_developer_id_list,             # 前端
                    'front_developer_list': ','.join(front_developer_list),         # 前端

                    'back_developer_id_list': back_developer_id_list,               # 后端
                    'back_developer_list': ','.join(back_developer_list),           # 后端

                    'oper_user__username': oper_user_username,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
            language_type = []
            for i in models.caseInterProject.language_type_choices:
                language_type.append({
                    'id':i[0],
                    'name':i[1]
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'language_type':language_type
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

        # 添加测试用例项目
        if oper_type == "add":
            form_data = {
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),                       # 项目名称
                'language_type': request.POST.get('language_type'),     # 语言类型  区分请求结果
                'front_developer': request.POST.get('front_developer'), # 前端开发人员
                'back_developer': request.POST.get('back_developer'),   # 后端开发人员
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)

                #  添加数据库
                obj = caseInterProject_obj = models.caseInterProject.objects.create(
                    name=forms_obj.cleaned_data['name'],
                    oper_user_id=forms_obj.cleaned_data['oper_user_id'],
                    language_type=forms_obj.cleaned_data['language_type'],
                )

                caseInterProject_obj.front_developer = json.loads(forms_obj.cleaned_data['front_developer'])
                caseInterProject_obj.back_developer = json.loads(forms_obj.cleaned_data['back_developer'])
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改测试用例项目
        elif oper_type == "update":
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'front_developer': request.POST.get('front_developer'),  # 前端
                'back_developer': request.POST.get('back_developer'),    # 后端
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
                    objs[0].front_developer = json.loads(forms_obj.cleaned_data['front_developer'])
                    objs[0].back_developer = json.loads(forms_obj.cleaned_data['back_developer'])
                    objs[0].save()
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除测试用例项目
        elif oper_type == "delete":
            form_data = {
                'o_id':o_id
            }
            forms_obj = DeleteForm(form_data)
            if forms_obj.is_valid():
                models.caseInterProject.objects.filter(id=o_id).delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        if oper_type =='getTaskName':
            objs = models.caseInterProject.objects.filter(back_developer=user_id)
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
