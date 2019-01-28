from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.caseInterfaceGrouping import AddForm, UpdateForm, SelectForm, DeleteForm
import json
from django.db.models import Q

# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def testCaseGroup(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'talk_project_id': '',
                'parensGroupName': '',
                'operUser_id': '',
                'groupName': '__contains',
            }

            print('=--=--')
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.caseInterfaceGrouping.objects.select_related('talk_project').filter(
                q,
                talk_project__back_developer=user_id
            ).order_by(order).order_by('create_date')
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
                talk_project_id = ''
                if obj.talk_project:
                    talkName = obj.talk_project.name
                    talk_project_id = obj.talk_project_id
                ret_data.append({
                    'id': obj.id,
                    'groupName': obj.groupName,
                    'parensGroupName_id':parensGroupName_id,
                    'parensGroupName': parensGroupName,
                    'operUser': obj.operUser.username,
                    'operUser_id':obj.operUser.id,
                    'talk_project_id':talk_project_id,
                    'talkProject': talkName,
                    'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'count': count,
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)

# o_id 判断是否会关联自己 如果o_id 在 result_data里会return
def updateInitData(result_data, talk_project_id, pid=None, o_id=None):
    objs = models.caseInterfaceGrouping.objects.filter(
        talk_project_id=talk_project_id,
        id=pid,
    )
    for obj in objs:
        print('obj.id-----------> ',obj.id)
        result_data.append(obj.id)
        if o_id:
            if int(o_id) == int(obj.id):
                return result_data
        parent = updateInitData(result_data, talk_project_id, pid=obj.parensGroupName_id, o_id=o_id)
    return result_data


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def testCaseGroupOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    form_data = {
        'o_id':o_id,
        'operUser_id': request.GET.get('user_id'),                   # 操作人
        'groupName': request.POST.get('groupName'),                  # 分组名称
        'parensGroupName': request.POST.get('parensGroupName'),      # 父级分组名称
        'talk_project_id': request.POST.get('talk_project_id'),      # 归属项目
    }
    operUser_id = form_data.get('operUser_id')
    userObjs = models.caseInterfaceGrouping.objects
    q = Q()
    q.add(Q(front_developer=operUser_id) | Q(back_developer=operUser_id), Q.AND)
    projectObjs = models.caseInterProject.objects.filter(q)

    if request.method == "POST":

        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                if userObjs:
                    formResult = forms_obj.cleaned_data
                    parensGroupName = formResult.get('parensGroupName')
                    level = 1
                    if parensGroupName:
                        level = 2
                        objs = models.caseInterfaceGrouping.objects.filter(id=formResult.get('parensGroupName'))
                        if not objs:
                            response.code = 402
                            response.msg = '无此父级分组'
                            return JsonResponse(response.__dict__)

                    objs = models.caseInterfaceGrouping.objects
                    obj = objsId = objs.create(
                        groupName=formResult.get('groupName'),
                        parensGroupName_id=parensGroupName,
                        operUser_id=formResult.get('operUser_id'),
                        talk_project_id=formResult.get('talk_project_id')
                    )
                    objs.filter(id=objsId.id).update(level=level)
                    response.code = 200
                    response.msg = "添加成功"
                    response.data = {'testCase': obj.id}
            else:
                print("GROUP 添加 验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "update":
            # 获取需要修改的信息
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                #  查询数据库  用户id
                formResult = forms_obj.cleaned_data
                objs = userObjs.filter(id=formResult.get('o_id'))
                if objs:
                    result_data = []
                    talk_project_id = formResult.get('talk_project_id')
                    if formResult.get('parensGroupName'):
                        if int(o_id) == int(formResult.get('parensGroupName')):
                            response.code = 301
                            response.msg = '不可关联自己'
                            return JsonResponse(response.__dict__)
                        parentObjs = userObjs.filter(id=formResult.get('parensGroupName'))
                        parentData = updateInitData(result_data, talk_project_id, parentObjs[0].parensGroupName_id, o_id)
                        if int(o_id) in parentData:
                            response.code = 301
                            response.msg = '不可关联自己'
                            return JsonResponse(response.__dict__)
                    objs.filter(id=o_id).update(
                        groupName=formResult.get('groupName'),
                        parensGroupName_id=formResult.get('parensGroupName'),
                        operUser_id=formResult.get('operUser_id'),
                        talk_project_id=formResult.get('talk_project_id')
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("GROUP 修改 验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            forms_obj = DeleteForm(form_data)
            if forms_obj.is_valid():
                # 删除 ID
                models.caseInterfaceGrouping.objects.filter(id=o_id).delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                print("GROUP 删除 验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        # 查询 当前登录人 全部项目
        if oper_type == 'selectTalkName':
            otherData = []
            for projectObj in projectObjs:
                otherData.append({
                    'id': projectObj.id,
                    'taskName':projectObj.name
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'otherData':otherData
            }

        # 查询当前登录人 所有上级分组
        elif oper_type == 'superGroupName':
            # talkIdList = [i['id'] for i in projectObjs.values('id')]
            # print('talkIdList------> ',talkIdList)
            objs = models.caseInterfaceGrouping.objects.filter(operUser_id=operUser_id)
            data_list = []
            for obj in objs:
                data_list.append({
                    'id': obj.id,
                    'name':obj.groupName
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'data_list':data_list}

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
