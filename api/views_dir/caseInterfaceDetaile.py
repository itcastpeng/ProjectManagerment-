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
import datetime, requests

# 分组  树状图
def testCaseGroupTree(talkProject_id, operUser_id, pid=None, selected_list=None):
    result_data = []
    objs = models.caseInterfaceGrouping.objects.filter(operUser_id=operUser_id).filter(talkProject_id=talkProject_id).filter(parensGroupName_id=pid)
    for obj in objs:
        current_data = {
            'groupName': obj.groupName,
            'expand': True,
            'id': obj.id,
            'checked': False
        }
        if selected_list and obj.id in selected_list:
            current_data['checked'] = True
        children_data = testCaseGroupTree(talkProject_id, operUser_id, obj.id, selected_list)
        if children_data:
            current_data['children'] = children_data
        result_data.append(current_data)

    return result_data




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
            order = request.GET.get('order', '-create_date')
            beforeTaskId = request.GET.get('beforeTaskId')          # 最开始传来的项目ID
            user_id = request.GET.get('user_id')                    # 用户ID
            # caseName = request.GET.get('caseName')                  # 搜索条件
            # ownershipGroup = request.GET.get('ownershipGroup')                  # 分组
            field_dict = {
                'id': '',
                'ownershipGroup': '__contains',
                'url': '',
                'caseName': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.caseInterfaceDetaile.objects.filter(ownershipGroup__talkProject_id=beforeTaskId).filter(q).order_by(order)
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
                   'ownershipGroup': obj.ownershipGroup.groupName,
                   'url':obj.url,
                   'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                   'user_id': obj.userProfile.id,
                   'username': obj.userProfile.username,
                   'requestType':obj.get_requestType_display(),
                   'jieKouName': obj.caseName,
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
    # print('request.GET--------> ',request.GET)
    # print('request.POST=========> ', request.POST)
    form_data = {
        'o_id':o_id,
        'url': request.POST.get('url'),                   # url
        'user_id': request.GET.get('user_id'),                   # 操作人
        'ownershipGroup_id': request.POST.get('ownershipGroup_id'),     # 分组名称
        'hostManage_id': request.POST.get('hostManage_id'),         # host
        'requestType': request.POST.get('requestType'),             # 请求类型 1 GET 2 POST
        'caseName': request.POST.get('caseName'),                   # 接口名称
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
                    ownershipGroup_id=formResult.get('ownershipGroup_id'),
                    hostManage_id=formResult.get('hostManage_id'),
                    requestType=formResult.get('requestType'),
                    caseName=formResult.get('caseName'),
                    userProfile_id=form_data.get('user_id')
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

        elif oper_type == "delete":
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

        elif oper_type == 'sendTheRequest':
            add = request.GET.get('add')
            print(request.GET)
            requestType = request.GET.get('requestType')
            requestUrl = request.GET.get('requestUrl')
            postRequest = request.GET.get('postRequest')
            getRequest = request.GET.get('getRequest')
            canshu = ''
            number = 0
            json_data = []
            statusCode = 500
            if getRequest:
                get = json.dumps(eval(getRequest))
                for key, value in json.loads(get).items():
                    number += 1
                    if number > 1:
                        canshu += '&' + key + '=' + value
                    else:
                        canshu += '?' + key + '=' + value
                requestsURL = requestUrl + canshu
                ret = requests.get(requestsURL)
                json_data = json.loads(ret.text)
                statusCode = ret.status_code

            data_list = {}
            if postRequest:
                post = json.dumps(eval(postRequest))
                requestsURL = requestUrl
                if getRequest:
                    requestsURL = requestUrl + canshu
                if requestType and int(requestType) == 2:
                    for i, data in  json.loads(post).items():
                        data_list[i] = data
                    ret = requests.post(requestsURL, data=data_list)
                    json_data = json.loads(ret.text)
                    statusCode = ret.status_code
            if add:
                forms_obj = AddForm(form_data)
                if forms_obj.is_valid():
                    formResult = forms_obj.cleaned_data
                    detaileObjs.create(
                        url=requestUrl,
                        ownershipGroup_id=formResult.get('ownershipGroup_id'),
                        hostManage_id=formResult.get('hostManage_id'),
                        requestType=requestType,
                        caseName=formResult.get('caseName'),
                        userProfile_id=form_data.get('user_id'),
                        getRequestParameters=canshu,
                        postRequestParameters=data_list
                    )
                    response.code = 200
                    response.msg = '添加成功'
                    response.data = {}
                else:
                    print("验证不通过")
                    # print(forms_obj.errors)
                    response.code = 301
                    # print(forms_obj.errors.as_json())
                    response.msg = json.loads(forms_obj.errors.as_json())
            else:
                response.code = statusCode
                response.msg = '请求成功'
                response.data = {'requestResult': json_data}
    else:
        if oper_type == 'getTaskName':
            objs = models.project.objects.all()
            otherData = []
            for obj in objs:
                otherData.append({
                    'id':obj.id,
                    'name': obj.name
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData':otherData}

        elif oper_type == 'getOrPostRequest':
            objs = models.caseInterfaceDetaile.status_choices
            otherData = []
            for obj in objs:
                otherData.append({
                    'id':obj[0],
                    'name':obj[1]
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData':otherData}

        elif oper_type == 'blockTree':
            beforeTaskId = request.GET.get('beforeTaskId')
            user_id = form_data.get('user_id')
            groupobjs = models.caseInterfaceGrouping.objects.filter(operUser_id=user_id).filter(
                talkProject_id=beforeTaskId).filter(parensGroupName__isnull=True)
            selected_list = [i.id for i in groupobjs]
            result = testCaseGroupTree(beforeTaskId, user_id, selected_list=selected_list)
            response.code = 200
            response.msg = '查询成功'
            response.data = {'result': result}

        else:
            response.code = 402
            response.msg = "请求异常"


    return JsonResponse(response.__dict__)