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
import datetime, requests, random
from django.db.models import Q

pcRequestHeader = [
    'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.16) Gecko/20101130 Firefox/3.5.16',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; .NET CLR 1.1.4322)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-CN; rv:1.9.0.19) Gecko/2010031422 Firefox/3.0.19 (.NET CLR 3.5.30729)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
]

# 分组  树状图
def testCaseGroupTree(talkProject_id, operUser_id, pid=None):
    result_data = []
    objs = models.caseInterfaceGrouping.objects.filter(operUser_id=operUser_id).filter(talkProject_id=talkProject_id).filter(parensGroupName_id=pid)
    for obj in objs:
        current_data = {
            'groupName': obj.groupName,
            'expand': True,
            'id': obj.id,
            'checked': False
        }
        children_data = testCaseGroupTree(talkProject_id, operUser_id, obj.id)
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
                print("formResult.get('url')=========> ", formResult.get('url'))
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
            add = request.POST.get('add')
            requestType = request.POST.get('requestType')
            requestUrl = request.POST.get('requestUrl')
            postRequest = request.POST.get('postRequest')
            getRequest = request.POST.get('getRequest')
            canshu = ''
            number = 0
            json_data = []
            if int(o_id) > 0:  # 单独查询
                objs = models.caseInterfaceDetaile.objects.filter(id=o_id)
                postRequest = objs[0].postRequestParameters
                requestUrl = objs[0].url
                requestType = objs[0].requestType
            if requestUrl:
                if requestType and int(requestType) == 1:
                    requestsURL = requestUrl
                    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)], }
                    if getRequest:
                        for get in eval(getRequest):
                            for key, value in get.items():
                                number += 1
                                if number > 1:
                                    canshu += '&' + key + '=' + value
                                else:
                                    canshu += '?' + key + '=' +value
                            requestsURL = requestUrl + canshu
                    ret = requests.get(requestsURL, headers=headers)
                    if 'www' in requestUrl:
                        json_data = ret.content.decode(encoding='utf8')
                    else:
                        # print(ret.content)
                        try:
                            json_data = json.loads(ret.content)
                        except Exception:
                            json_data = ret.content

                else:
                    data_list = {}
                    requestsURL = requestUrl
                    if postRequest:
                        for post in eval(postRequest):
                            if getRequest:
                                requestsURL = requestUrl + canshu
                            if requestType and int(requestType) == 2:
                                for key, value in post.items():
                                    data_list[key] = value
                            ret = requests.post(requestsURL, data=data_list)
                            json_data = json.loads(ret.text)
                    else:
                        response.code = 301
                        response.msg = '如果是POST请求, 请输入POST参数！'
                        response.data = ''
                        return JsonResponse(response.__dict__)
                if add:
                    forms_obj = AddForm(form_data)
                    if forms_obj.is_valid():
                        formResult = forms_obj.cleaned_data
                        hostManage_id = formResult.get('hostManage_id')
                        ownershipGroup_id = formResult.get('ownershipGroup_id')
                        hostObjs = models.configurationManagementHOST.objects.filter(id=hostManage_id)
                        groupObjs = models.caseInterfaceGrouping.objects.filter(id=ownershipGroup_id)
                        if not hostObjs or not groupObjs:
                            response.data = ''
                            response.code = 301
                            if not hostObjs:
                                response.msg = 'HOST错误！'
                            if not groupObjs:
                                response.msg = '分组错误！'
                            return JsonResponse(response.__dict__)
                        if add != 'add':
                            if add.isdigit():
                                urlObjs = detaileObjs.filter(id=add)
                                if urlObjs:
                                    urlObjs.update(
                                        url=requestUrl,
                                        requestType=requestType,
                                        getRequestParameters=getRequest,
                                        postRequestParameters=postRequest,
                                        ownershipGroup_id=formResult.get('ownershipGroup_id'),
                                        caseName=formResult.get('caseName'),
                                        userProfile_id=form_data.get('user_id'),
                                        hostManage_id=hostManage_id,
                                    )
                                    response.msg = '修改成功'
                                else:
                                    response.code = 301
                                    response.msg = '要修改的URL错误'
                                    response.data = ''
                                    return JsonResponse(response.__dict__)
                            else:
                                response.code = 301
                                response.msg = '修改的urlId请传INT类型！'
                                response.data = ''
                                return JsonResponse(response.__dict__)
                        else:
                            detaileObjs.create(
                                url=requestUrl,
                                requestType=requestType,
                                getRequestParameters=getRequest,
                                postRequestParameters=postRequest,
                                ownershipGroup_id=formResult.get('ownershipGroup_id'),
                                caseName=formResult.get('caseName'),
                                userProfile_id=form_data.get('user_id'),
                                hostManage_id=hostManage_id,
                            )
                            response.msg = '添加成功'
                        response.code = 200
                        response.data = {}
                    else:
                        print("验证不通过")
                        # print(forms_obj.errors)
                        response.code = 301
                        # print(forms_obj.errors.as_json())
                        response.msg = json.loads(forms_obj.errors.as_json())
                else:
                    response.code = 200
                    response.msg = '请求成功'
                    response.data = {
                        'responseData': json_data,
                    }
            else:
                response.code = 500
                response.msg = '请输入URL！'
                response.data = ''
            return JsonResponse(response.__dict__)
    else:
        # 获取 项目名称
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

        # 获取 GET和POST 请求
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

        # 左侧展示 树状图
        elif oper_type == 'blockTree':
            beforeTaskId = request.GET.get('beforeTaskId')
            user_id = form_data.get('user_id')
            result = testCaseGroupTree(beforeTaskId, user_id)
            response.code = 200
            response.msg = '查询成功'
            response.data = {'result': result}

        # 查询 host 展示
        elif oper_type == 'getHostYuMing':
            formalOrTest = request.GET.get('formalOrTest')
            q = Q()
            objs = models.configurationManagementHOST.objects.filter(q)
            if formalOrTest:
                if formalOrTest == 1:
                    q.add(Q(describe=1), Q.AND)
                else:
                    q.add(Q(describe=2), Q.AND)
            otherData = []
            for obj in objs:
                otherData.append({
                    'id':obj.id,
                    'name':obj.hostName,
                    'host':obj.hostUrl
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData': otherData}

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)

# 启用测试用例
@csrf_exempt
@account.is_token(models.userprofile)
def startTestCase(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        user_id = request.GET.get('user_id')
        talkProject_id = request.POST.get('talkProject_id')
        if talkProject_id:
            print('talkProject_id========> ',talkProject_id, user_id)
            objs = models.caseInterfaceDetaile.objects.select_related(
                'ownershipGroup__talkProject',
                'ownershipGroup__operUser'
            ).filter(
                ownershipGroup__talkProject_id=talkProject_id,
                ownershipGroup__operUser_id=user_id
            ).order_by('create_date')               # 按时间正序排列
            if objs:
                for obj in objs:
                    postRequest = obj.postRequestParameters
                    requestUrl = obj.url
                    requestType = obj.requestType
                    print('obj.id--------------> ',obj.id)
                    try:
                        if requestType:
                            if int(requestType) == 1:
                                print('GET 请求')
                                ret = requests.get(requestUrl)
                                ret.encoding = 'utf8'
                                json_data = json.loads(ret.text)
                                if json_data:
                                    if int(json_data.get('code')) != 200:
                                        response.code = 301
                                        response.msg = '当前返回状态码错误'
                                        response.data = {
                                            'code':json_data.get('code'),
                                            'url':requestUrl,
                                            'requestType':'GET'
                                        }
                                        return JsonResponse(response.__dict__)
                            else:
                                data_list = {}
                                print('POST 请求')
                                for post in eval(postRequest):
                                    for key, value in post.items():
                                        data_list[key] = value
                                ret = requests.post(requestUrl, data=data_list)
                                ret.encoding = 'utf8'
                                json_data = json.loads(ret.text)
                                if json_data:
                                    if int(json_data.get('code')) != 200:
                                        response.code = 301
                                        response.msg = '当前返回状态码错误'
                                        response.data = {
                                            'code': json_data.get('code'),
                                            'url': requestUrl,
                                            'requestType': 'POST'
                                        }
                                        return JsonResponse(response.__dict__)
                                continue
                    except Exception as error:
                        print('错误==!!!!!!!!=====-> ', error)
                        response.code = 301
                        response.msg = '内部错误'
                        response.data = {'error':error}
                response.code = 200
                response.msg = '通过'
            else:
                response.code = 301
                response.msg = '无测试用例可运行'
        else:
            response.code = 301
            response.msg = '无项目ID'
    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)



