from api import models
from publicFunc import Response
from publicFunc import account
from publicFunc.userAgente.user_agente import pcRequestHeader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.caseInterfaceDetaile import AddForm, UpdateForm, SelectForm, DeleteForm, AddTimingCase, DeleteTimingCase
from django.db.models import Q
import datetime, requests, random, json, re, redis
from api import  setting


# 分组树状图（包含测试用例详情）
def testCaseGroupTree(talk_project_id, pid=None, search_msg=None):
    result_data = []
    if search_msg: # 搜索分组名称
        objs = models.caseInterfaceGrouping.objects.filter(parensGroupName_id=pid, groupName__contains=search_msg)
    else:
        q = Q()
        objs = models.caseInterfaceGrouping.objects.filter(talk_project_id=talk_project_id, parensGroupName_id=pid)
    for obj in objs:
        current_data = {
            'title':obj.groupName,
            'expand': True,
            'id': obj.id,
            'checked': False,
            'file':True
        }
        children_data = testCaseGroupTree(talk_project_id, obj.id)
        detail_obj = models.caseInterfaceDetaile.objects.filter(ownershipGroup_id=obj.id)
        if detail_obj:
            for i in detail_obj:
                children_data.append({
                    'title': i.caseName,
                    'id': i.id,
                    'file': False
                })
        current_data['children'] = children_data
        result_data.append(current_data)
    return result_data

# 分组树状图（不包含测试用例详情）
def GroupTree(talk_project_id, operUser_id, pid=None):
    result_data = []
    objs = models.caseInterfaceGrouping.objects.filter(operUser_id=operUser_id).filter(talk_project_id=talk_project_id).filter(parensGroupName_id=pid)
    for obj in objs:
        current_data = {
            'title':obj.groupName,
            'expand': True,
            'id': obj.id,
            'checked': False,
            'file':True
        }
        children_data = testCaseGroupTree(talk_project_id, operUser_id, obj.id)
        current_data['children'] = children_data
        result_data.append(current_data)
    return result_data

# 查询当前分组下所有详情数据
def selectCaseDetailGroup(ownershipGroup_id, resultData):
    groupObjs = models.caseInterfaceGrouping.objects.filter(parensGroupName_id=ownershipGroup_id)
    if groupObjs:
        for obj in groupObjs:
            resultData.append(obj.id)
            selectCaseDetailGroup(obj.id, resultData)
    return resultData

# 发送请求
def sendRequest(formResult, test=None):
    response = Response.ResponseObj()
    o_id=formResult.get('o_id')                             # ID
    xieyi_type=formResult.get('xieyi_type')                 # 协议类型（http:https）
    hostManage_id, hostUrl=formResult.get('hostManage_id')  # host配置
    requestType=formResult.get('requestType')               # 请求类型（GET，POST）
    getRequestParameters=formResult.get('getRequest')       # GET参数
    postRequestParameters=formResult.get('postRequest')     # POST参数
    url=formResult.get('requestUrl')                        # URL
    type_status=formResult.get('type_status')               # 接口类型(增删改查)

    if xieyi_type and int(xieyi_type) == 1:
        xieyi_type = 'http'
    else:
        xieyi_type = 'https'

    # 拼接URL
    requestUrl = xieyi_type + '://' + hostUrl + url  # url

    # 修改 删除
    if type_status and int(type_status) in [2, 4]:
        print('-----------------> 修改 删除')
        detail_objs = models.caseInterfaceDetaile.objects
        objs = detail_objs.filter(id=o_id)
        if objs:
            group_obj = detail_objs.filter(ownershipGroup_id=objs[0].ownershipGroup_id, type_status=1)
            if group_obj:
                testCase = group_obj[0].testCase
                if testCase:
                    num = re.sub(r'\?.*$', "", requestUrl)
                    canshu = num[num.rfind('/'):]
                    requestUrl = requestUrl.replace(canshu.strip(), '/' + str(testCase))
                else:
                    response.code = 301
                    response.msg = '未找到testCase'
            else:
                response.code = 301
                response.msg = '未找到添加接口, 无操作ID'

    # 判断 GET / POST 请求
    if requestType == 1:
        print('GET-------------请求')
        ret = requests.get(requestUrl)
    else:
        print('POST-------------请求')
        postRequestParameters = eval(postRequestParameters)
        data = {}
        for i in postRequestParameters:
            data[i['key']] = i['value']
        ret = requests.post(requestUrl, data=data)
    flag = False  # 判断接口是否出错
    try:
        # 获取请求结果和code
        ret_json = ret.json()
        # 添加
        if type_status and int(type_status) == 1:
            print('-----------------> 添加')
            testCase = ret_json.get('data').get('testCase')  # 添加返回的ID
            if testCase:
                objs = models.caseInterfaceDetaile.objects.filter(id=o_id)
                if objs:
                    objs[0].testCase = testCase
                    objs[0].save()
            else:
                response.code = 301
                response.msg = '添加接口未返回testCase'
    except Exception:
        flag = True
        ret_json = ret.text

    # 创建日志  (每个接口只记录最后一次请求数据)
    if not test:
        objs = models.requestResultSave.objects.filter(case_inter_id=o_id)
        data = {
            'url':requestUrl,
            'result_data':json.dumps(ret_json)
        }
        if objs:
            data['create_date'] = datetime.datetime.now()
            objs.update(**data)
        else:
            data['case_inter_id'] = o_id
            objs.create(**data)
    response.code = 200
    response.msg = '请求成功'
    response.data = {
        'ret_json':ret_json,
        'flag':flag,
        'requestUrl':requestUrl
    }
    # print('response.data---------> ', response.data)
    return response

# 自动测试 发送请求
def automaticTest(data_dict):
    url = '{}/api/startTestCase?beforeTaskId=2&rand_str=f2dd5cd6544a39a82d437bfa1bf8216a&timestamp=1547013904167&user_id=7'.format(setting.host)
    print("data_dict['case_inter_result']------------------> ", data_dict['case_inter_result'], type(data_dict['case_inter_result']))
    data = {
        'case_id_list':str(data_dict['case_inter_result']),         # 分组ID列表
        'talk_project_id':data_dict['talk_project_id'],             # 项目ID
        'is_generate':1,                                            # 是否生成文档
        'is_automatic_test':1                                       # 是否为机器测试
    }
    print('data--> ', data)
    requests.post(url, data=data)


# cerf  token验证 测试用例展示模块
@csrf_exempt
@account.is_token(models.userprofile)
def testCaseDetaile(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            beforeTaskId = request.GET.get('beforeTaskId')          # 最开始传来的项目ID
            ownershipGroup_id = request.GET.get('ownershipGroup_id')                  # 分组
            field_dict = {
                'id': '',
                'url': '',
                'caseName': '__contains',
                'ownershipGroup': '__contains',  # 分组
                'userProfile_id': '',
                'create_date': '__contains',
            }
            q = conditionCom(request, field_dict)
            # 如果选中分组 查询该分组下 所有详情
            if ownershipGroup_id:
                resultData = []
                resultList = selectCaseDetailGroup(ownershipGroup_id, resultData)
                resultList.append(ownershipGroup_id)
                q.add(Q(ownershipGroup_id__in=resultList), Q.AND)

            print('q -->', q)
            objs =  models.caseInterfaceDetaile.objects.filter(ownershipGroup__talk_project_id=beforeTaskId).filter(q).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            # 返回的数据
            ret_data = []
            history_date = {}
            if objs:
                obj = objs[0]

                hostManage_id = ''
                if obj.hostManage:
                    hostManage_id = obj.hostManage.id

                getRequestParameters = '[]'         # GET请求参数
                if obj.getRequestParameters:
                    getRequestParameters = obj.getRequestParameters

                postRequestParameters = '[]'        # POST请求参数
                if obj.getRequestParameters:
                    postRequestParameters = obj.postRequestParameters

                requestType_id = ''                 # 请求类型GET/POST
                requestType = ''
                if obj.requestType:
                    requestType_id = obj.requestType
                    requestType = obj.get_requestType_display()

                xieyi_type_id = ''                  # 协议 HTTP
                xieyi_type = ''
                if obj.xieyi_type:
                    xieyi_type_id = obj.xieyi_type
                    xieyi_type = obj.get_xieyi_type_display()

                type_status_id = ''                 # 接口类型(增删改查)
                type_status = ''
                if obj.type_status:
                    type_status_id = obj.type_status
                    type_status = obj.get_type_status_display()

                requestUrl = ''                     # URL
                if obj.url:
                    requestUrl = obj.url

                # =------------------------------------------历史请求------------------------
                history_objs = models.requestResultSave.objects.filter(case_inter_id=obj.id)
                if history_objs:
                    history_obj = history_objs[0]
                    result_data = ''
                    if history_obj.result_data:
                        try:
                            result_data = json.loads(history_obj.result_data)
                        except Exception:
                            result_data = history_obj.result_data
                    history_date = {
                        'url':history_obj.url,                                  # 历史请求URL
                        'result_data':result_data,                              # 历史请求 结果
                        'create_date':history_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    }

                ret_data.append({
                   'id': obj.id,

                    'ownershipGroup_id': obj.ownershipGroup_id,
                    'ownershipGroup': obj.ownershipGroup.groupName,

                    'oper_user_id': obj.userProfile.id,
                    'oper_user__username': obj.userProfile.username,

                    'requestUrl':requestUrl,
                    'caseName': obj.caseName,                               # 接口名称

                    'hostManage_id': hostManage_id,                         # host

                    'getRequestParameters': getRequestParameters,           # GET参数
                    'postRequestParameters': postRequestParameters,         # POST参数

                    'requestType_id': requestType_id,                       # 请求类型  (GET/POST)
                    'requestType': requestType,

                    'xieyi_type_id': xieyi_type_id,                         # 协议类型   (HTTP)
                    'xieyi_type': xieyi_type,

                    'type_status_id': type_status_id,                       # 接口类型   (增删改查)
                    'type_status': type_status,

                    'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'), # 接口创建时间
               })

                #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'history_date':history_date
            }
        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def testCaseDetaileOper(request, oper_type, o_id):
    response = Response.ResponseObj()
    form_data = {
        'o_id':o_id,
        'oper_user_id': request.GET.get('user_id'),                 # 操作人

        'ownershipGroup_id': request.POST.get('ownershipGroup_id'), # 分组名称
        'caseName': request.POST.get('caseName'),                   # 接口名称

        'requestUrl': request.POST.get('requestUrl'),               # url
        'hostManage_id': request.POST.get('hostManage_id'),         # host
        'requestType': request.POST.get('requestType'),             # 请求类型 1 GET 2 POST
        'type_status': request.POST.get('type_status'),             # 接口类型 (增删改查)
        'xieyi_type': request.POST.get('xieyi_type'),               # 协议类型 (http : https)

        'getRequest': request.POST.get('getRequest'),               # GET  请求参数
        'postRequest': request.POST.get('postRequest'),             # POST 请求参数
    }
    # print('form_data--> ', form_data)
    detaileObjs = models.caseInterfaceDetaile.objects
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 增加测试用例
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                formResult = forms_obj.cleaned_data
                # 默认值  首次添加可为空
                type_status = formResult.get('type_status')
                if not formResult.get('type_status'):
                    type_status = 1

                obj = detaileObjs.create(
                    caseName=formResult.get('caseName'),                        # 接口名称 (别名)
                    ownershipGroup_id=formResult.get('ownershipGroup_id'),      # 分组名称
                    userProfile_id=form_data.get('oper_user_id'),               # 操作人
                    hostManage_id=formResult.get('hostManage_id'),              # host配置

                    xieyi_type=1,                                               # 协议(默认HTTP)
                    requestType=1,                                              # 请求类型（GET，POST）(默认GET)
                    type_status=type_status,                                    # 接口类型（增删改查）

                )
                response.code = 200
                response.msg = '添加成功'
                response.data = {'testCase': obj.id}

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除测试用例
        elif oper_type == "delete":
            forms_obj = DeleteForm(form_data)
            if forms_obj.is_valid():
                models.requestDocumentDoc.objects.filter(interDetaile_id=o_id).delete()  # 删除文档
                models.caseInterfaceDetaile.objects.filter(id=o_id).delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 发送请求和保存
        elif oper_type == 'sendTheRequest':
            print('---------------测试')
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                formResult = forms_obj.cleaned_data
                try:
                    response_data = sendRequest(formResult)

                    if response_data.data.get('flag'):
                        response.msg = '接口出错了'
                        response.data = str(response_data.data.get('ret_json'))
                    else:
                        response_data_code = response_data.data.get('ret_json').get('code')
                        if response_data_code and int(response_data_code) == 200:
                            response.msg = '测试/保存 成功'
                        else:
                            response.code = 200
                            response.msg = '测试失败 / 保存成功'
                        response.data = response_data.data.get('ret_json')
                        print('response_data--> ', response_data.data.get('ret_json'))

                        # 保存数据 -------------------------------------------------------
                        formResult = forms_obj.cleaned_data
                        hostManage_id, hostUrl = formResult.get('hostManage_id')
                        detaileObjs.filter(id=o_id).update(
                            caseName=formResult.get('caseName'),  # 接口名称 (别名)
                            ownershipGroup_id=formResult.get('ownershipGroup_id'),  # 分组名称
                            userProfile_id=form_data.get('oper_user_id'),  # 操作人

                            hostManage_id=hostManage_id,  # host配置
                            requestType=formResult.get('requestType'),  # 请求类型（GET，POST）
                            type_status=formResult.get('type_status'),  # 接口类型（增删改查）
                            xieyi_type=formResult.get('xieyi_type'),  # 协议类型（http:https）

                            getRequestParameters=formResult.get('getRequest'),  # GET参数
                            postRequestParameters=formResult.get('postRequest'),  # POST参数
                            url=formResult.get('requestUrl'),  # URL
                        )
                        # ----------------------------------------------------------------------

                except Exception:
                    response.msg = '请求错误'
                response.code = 200

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            return JsonResponse(response.__dict__)

        # 添加定时运行测试用例(自动测试)
        elif oper_type == 'add_timing_case':
            case_inter_result = request.POST.get('case_inter_result')   # 要运行的分组ID列表
            run_type = request.POST.get('run_type')
            expect_run_time = request.POST.get('expect_run_time')       # 预计运行时间 (每天几点执行)
            expect_time = request.POST.get('expect_time')               # 时间段运行 (多久执行一次)

            form_data = {
                'user_id':user_id,
                'case_inter_result': case_inter_result,
                'run_type': run_type,
                'expect_run_time': expect_run_time,     # 预计运行时间 (每天几点执行)
                'expect_time': expect_time,             # 时间段运行 (多久执行一次)
            }
            forms_obj = AddTimingCase(form_data)
            if forms_obj.is_valid():
                form_data = forms_obj.cleaned_data
                print("验证通过")

                run_type, expect_run_time, expect_time = form_data.get('run_type')
                case_inter_result = form_data.get('case_inter_result')

                models.timingCaseInter.objects.create(**{
                    'run_type':run_type,
                    'expect_run_time':expect_run_time,
                    'expect_time':expect_time,
                    'case_inter_result':case_inter_result,
                    'userProfile_id':user_id,
                })
                response.code = 200
                response.msg = '添加成功'
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除定时运行测试用例(自动测试)
        elif oper_type == 'delete_timing_case':
            form_data = {
                'user_id':user_id,
                'o_id':o_id,
            }
            forms_obj = DeleteTimingCase(form_data)
            if forms_obj.is_valid():
                print('验证通过')
                models.timingCaseInter.objects.filter(id=o_id).delete()
                response.code = 200
                response.msg = '删除成功'
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # selenium 测试 添加日志
        elif oper_type == 'selenium_log_add':
            title = request.POST.get('title')
            remak = request.POST.get('remak')
            if_success = request.POST.get('if_success')
            if title and remak:
                success = 0
                if if_success and int(if_success) == 1:
                    success = 1
                models.selenium_test_doc.objects.create(**{
                    'title':title,
                    'remak':remak,
                    'if_success':success
                })
                response.code = 200
                response.msg = '添加成功'
            else:
                response.code = 301
                response.msg = '添加失败'

    else:
        # 获取项目名称
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

        # 获取 所有choices
        elif oper_type == 'get_choices':

            otherData = []  # 请求类型 GET POST
            for obj in models.caseInterfaceDetaile.status_choices:
                otherData.append({
                    'id':obj[0],
                    'name':obj[1]
                })

            xieyiData = []  # 协议 HTTP HTTPS
            for obj in models.caseInterfaceDetaile.xieyi_type_choices:
                xieyiData.append({
                    'id':obj[0],
                    'name':obj[1]
                })

            jiekouTypeData = []     # 接口类型 (增删改查)
            for obj in models.caseInterfaceDetaile.type_status_choices:
                jiekouTypeData.append({
                    'id':obj[0],
                    'name':obj[1]
                })

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'otherData':otherData,
                'xieyiData':xieyiData,
                'jiekouTypeData':jiekouTypeData,
            }

        # 左侧展示树状图（包含测试用例详情）
        elif oper_type == 'blockTree':
            beforeTaskId = request.GET.get('beforeTaskId')  # 项目ID
            if beforeTaskId:
                search_msg = request.GET.get('search_msg')      # 搜索分组名称
                if search_msg:# 搜索分组名称
                    result = testCaseGroupTree(beforeTaskId, search_msg=search_msg)
                else:
                    result = testCaseGroupTree(beforeTaskId)

                response.code = 200
                response.msg = '查询成功'
                response.data = {'result': result}

        # 展示树状图（不包含测试用例详情）(供自动测试选择)
        elif oper_type == 'treeGroup':
            beforeTaskId = request.GET.get('beforeTaskId')  # 项目ID
            result = GroupTree(beforeTaskId, user_id)
            response.code = 200
            response.msg = '查询成功'
            response.data = {'result': result}

        # 查询host展示
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
                    'name':obj.hostUrl
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {'otherData': otherData}

        # 查询测试用例(成功数量, 失败数量, 总数量)数据是否请求成功 结果说明
        elif oper_type == 'get_redis_result':
            rc = redis.Redis(host='redis_host', port=6379, db=0)
            get_keys = rc.hmget('testcase', 'num', 'error_num', 'success_num')
            success_num = int(get_keys[2].decode())
            objs = models.requestDoc.objects.filter(
                userProfile_id=user_id, create_date__isnull=False
            ).order_by('-create_date')[:success_num]
            data_list = []
            for obj in objs:
                data_list.append({
                    'name':obj.name,
                    'if_success':obj.if_success,
                    'result_data':json.loads(obj.result_data),
                    'userProfile_id':obj.userProfile_id,
                    'userProfile__name':obj.userProfile.username,
                    'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'data_list':data_list,
                'num': int(get_keys[0].decode()),  # 总数
                'error_num': int(get_keys[1].decode()),  # 错误
                'success_num': success_num,
            }

        # 查询测试用例 展示全部(同 selenium 测试 展示 统计)
        elif oper_type == 'get_test_result':
            forms_obj = SelectForm(request.GET)
            if not forms_obj.is_valid():
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            else:
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')
                field_dict = {
                    'id': '',
                    'url': '',
                    'if_success': '',
                    'is_automatic_test': '',
                    'userProfile_id': '',
                    'create_date': '__contains',
                }
                q = conditionCom(request, field_dict)
                objs = models.requestDoc.objects.filter(q).order_by(order)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                data_list = []

                for obj in objs:
                    data_list.append({
                        'name':obj.name,
                        'if_success':obj.if_success,
                        'result_data':json.loads(obj.result_data),

                        'userProfile_id':obj.userProfile_id,
                        'userProfile':obj.userProfile.username,
                        'is_automatic_test_id':obj.is_automatic_test,
                        'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'data_list':data_list,
                    'is_automatic_test_choices':models.requestDoc.is_automatic_test_choices
                }

        # 查看自动测试数据
        elif oper_type == 'get_timing_case_result':
            objs = models.timingCaseInter.objects.filter(userProfile_id=user_id).order_by('-create_date')
            data_list = []
            for obj in objs:
                run_time = ''
                if obj.run_time:
                    run_time = obj.run_time.strftime('%Y-%m-%d %H:%M:%S')

                data_list.append({
                    'case_inter_result':json.loads(obj.case_inter_result),

                    'run_type_id':obj.run_type,
                    'run_type':obj.get_run_type_display(),

                    'expect_time':obj.expect_time,              # 时间段运行
                    'expect_run_time':obj.expect_run_time,      # 预计运行时间

                    'run_time':run_time,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'data_list':data_list,
                'run_type_choises':models.timingCaseInter.run_type_choises
            }

        # 异步执行任务(自动测试)(celery调用)
        elif oper_type == 'automatic_test':
            objs = models.timingCaseInter.objects.filter(create_date__isnull=False, run_type__isnull=False)
            for obj in objs:
                now = datetime.datetime.now()
                case_inter_result = json.loads(obj.case_inter_result)
                group_obj = models.caseInterfaceGrouping.objects.filter(id=case_inter_result[0])
                talk_project_id = group_obj[0].talk_project_id
                data_dict = {
                    'talk_project_id':talk_project_id,
                    'case_inter_result':case_inter_result,
                }

                if not obj.run_time:
                    automaticTest(data_dict)
                    obj.run_time = (now + datetime.timedelta(days=1))
                    obj.save()
                else:

                    if int(obj.run_type) == 1 and obj.expect_run_time:
                        expect_run_time = datetime.datetime.strptime(obj.expect_run_time, '%H:%M:%S')
                        run_time = datetime.datetime.strptime(obj.run_time.strftime('%Y-%m-%d'), '%Y-%m-%d')
                        if run_time <= now and expect_run_time <= now:
                            automaticTest(data_dict)
                            obj.run_time = (now + datetime.timedelta(days=1))
                            obj.save()

                    elif int(obj.run_type) == 2 and obj.expect_time:
                        run_time = (obj.run_time + datetime.timedelta(minutes=int(obj.expect_time)))
                        if run_time <= now :
                            automaticTest(data_dict)
                            obj.run_time = now
                            obj.save()

                    else:
                        print('-----------执行错误')
            response.code = 200
            response.msg = '执行完成'

        # selenium 日志 查询
        elif oper_type == 'selenium_get':
            objs= models.selenium_test_doc.objects.filter(create_date__isnull=False)
            data_list = []
            for obj in objs:
                data_list.append({
                    'title':obj.title,
                    'remak':obj.remak,
                    'if_success':obj.if_success,
                    'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = data_list

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# 启用测试用例
@csrf_exempt
@account.is_token(models.userprofile)
def startTestCase(request):
    rc = redis.Redis(host='redis_host', port=6379, db=0)
    response = Response.ResponseObj()
    response.code = 200
    response.data = []
    if request.method == 'POST':
        user_id = request.GET.get('user_id')
        is_generate = request.POST.get('is_generate')               # 是否生成开发文档
        talk_project_id = request.POST.get('talk_project_id')       # 项目ID
        is_automatic_test = request.POST.get('is_automatic_test')   # 是否为机器测试
        case_id_list = request.POST.get('case_id_list')             # 选择分组传递分组ID列表
        num = 0         # 测试 总数
        error_num = 0   # 测试失败总数
        error_data = []
        success_num = 0
        flag = False        # 判断该接口是否有问题

        automatic_test = 2
        if is_automatic_test:
            automatic_test = 1

        if talk_project_id and case_id_list:
            case_id_list = json.loads(case_id_list)
            result_data = ''
            for i in case_id_list:
                objs = models.caseInterfaceDetaile.objects.filter(
                    ownershipGroup_id=i
                ).order_by('type_status')           # 按接口类型正序排列
                for obj in objs:                    # 遍历接口
                    id = obj.id                     # ID
                    requestUrl = obj.url            # URL
                    xieyi_type = obj.xieyi_type     # 协议 (HTTP)
                    hostManage = obj.hostManage     # HOST
                    requestType = obj.requestType   # 请求类型 (GET/POST)
                    type_status = obj.type_status   # 接口类型 (增删改查)
                    if id and requestUrl and xieyi_type and hostManage and type_status and requestType:
                        hostManage_id = obj.hostManage_id
                        hostUrl = obj.hostManage.hostUrl
                        getRequest = obj.getRequestParameters
                        postRequest = obj.postRequestParameters

                        data = {
                            'o_id':obj.id,
                            'xieyi_type':xieyi_type,
                            'hostManage_id':(hostManage_id, hostUrl),
                            'requestType':requestType,
                            'getRequest':getRequest,
                            'postRequest':postRequest,
                            'requestUrl':requestUrl,
                            'type_status':type_status,
                        }

                        response_data = sendRequest(data, test=1)
                        if response_data.data.get('flag'):
                            result_data = str(response_data.data.get('ret_json'))
                            flag = True
                        else:
                            code = response_data.data.get('ret_json').get('code')
                            result_data = response_data.data.get('ret_json')
                            if code and int(code) != 200:
                                flag = True
                                error_num += 1
                                error_data.append(result_data)
                            else:
                                success_num += 1

                        # 创建测试用例日志
                        if_success = 1
                        if flag:
                            if_success = 0
                        models.requestDoc.objects.create(**{
                            'name':obj.caseName,
                            'if_success':if_success,
                            'result_data':json.dumps(result_data),
                            'userProfile_id':obj.userProfile_id,
                            'is_automatic_test':automatic_test
                        })

                        if is_generate:
                            # 生成开发文档
                            data = {
                                'getRequestParameters': getRequest,
                                'postRequestParameters': postRequest,
                                'url':response_data.data.get('requestUrl'),
                                'jiekou_name':obj.caseName,
                                'talk_project_id':talk_project_id,
                                'requestType':requestType,
                                'result_data':json.dumps(result_data),
                                'create_date':datetime.datetime.now()
                            }
                            doc_obj = models.requestDocumentDoc.objects.filter(interDetaile_id=obj.id)
                            if doc_obj:
                                doc_obj.update(**data)
                            else:
                                data['interDetaile_id'] = obj.id
                                doc_obj.create(**data)
                    num += 1
                    redis_dict = {
                        'num':num,
                        'error_num':error_num,
                        'success_num':success_num
                    }
                    rc.hmset('testcase', redis_dict)

            response.msg = '测试完成'

        else:
            response.code = 301
            response.msg = '参数错误'

    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)

