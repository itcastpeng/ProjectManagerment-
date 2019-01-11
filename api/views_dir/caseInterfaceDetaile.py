from api import models
from publicFunc import Response
from publicFunc import account
from publicFunc.userAgente.user_agente import pcRequestHeader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.caseInterfaceDetaile import AddForm, UpdateForm, SelectForm, DeleteForm
from django.db.models import Q
import datetime, requests, random, json, re


# 分组树状图（包含测试用例详情）
def testCaseGroupTree(talk_project_id, operUser_id, pid=None, search_msg=None):
    result_data = []
    if search_msg: # 搜索分组名称
        objs = models.caseInterfaceGrouping.objects.filter(parensGroupName_id=pid, groupName__contains=search_msg)
    else:
        objs = models.caseInterfaceGrouping.objects.filter(operUser_id=operUser_id, talk_project_id=talk_project_id, parensGroupName_id=pid)
    for obj in objs:
        current_data = {
            'title':obj.groupName,
            'expand': True,
            'id': obj.id,
            'checked': False,
            'file':True
        }
        children_data = testCaseGroupTree(talk_project_id, operUser_id, obj.id)
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
            'result_data':ret_json
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
                    history_date = {
                        'url':history_obj.url,                          # 历史请求URL
                        'result_data':history_obj.result_data,          # 历史请求 结果
                        'create_date':history_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    }

                ret_data.append({
                   'id': obj.id,

                    'ownershipGroup_id': obj.ownershipGroup_id,
                    'ownershipGroup': obj.ownershipGroup.groupName,

                    'oper_user_id': obj.userProfile.id,
                    'oper_user__username': obj.userProfile.username,

                    'requestUrl':requestUrl,
                    'caseName': obj.caseName,                                # 接口名称

                    'hostManage_id': hostManage_id,                          # host

                    'getRequestParameters': getRequestParameters,        # GET参数
                    'postRequestParameters': postRequestParameters,      # POST参数

                    'requestType_id': requestType_id,                       # 请求类型  (GET/POST)
                    'requestType': requestType,

                    'xieyi_type_id': xieyi_type_id,                        # 协议类型   (HTTP)
                    'xieyi_type': xieyi_type,

                    'type_status_id': type_status_id,                      # 接口类型   (增删改查)
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
    print('form_data--> ', form_data)
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

        # 发送请求 和 保存
        elif oper_type == 'sendTheRequest':
            print('---------------测试')
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                formResult = forms_obj.cleaned_data
                response_data = sendRequest(formResult)
                response.code = 200
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
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            return JsonResponse(response.__dict__)

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
                    result = testCaseGroupTree(beforeTaskId, user_id, search_msg=search_msg)
                else:
                    result = testCaseGroupTree(beforeTaskId, user_id)
                response.code = 200
                response.msg = '查询成功'
                response.data = {'result': result}

        # 展示树状图（不包含测试用例详情）
        elif oper_type == 'treeGroup':
            beforeTaskId = request.GET.get('beforeTaskId')  # 项目ID
            result = GroupTree(beforeTaskId, user_id)
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
                    'name':obj.hostUrl
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
        is_generate = request.POST.get('is_generate')           # 是否生成开发文档
        talk_project_id = request.POST.get('talk_project_id')   # 项目ID
        case_id_list = request.POST.get('case_id_list')         # 选择分组 传递分组ID列表
        if talk_project_id and case_id_list:
            case_id_list = json.loads(case_id_list)
            flag = False
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
                                break
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
                            }
                            doc_obj = models.requestDocumentDoc.objects.filter(interDetaile_id=obj.id)
                            if doc_obj:
                                doc_obj.update(**data)
                            else:
                                data['interDetaile_id'] = obj.id
                                doc_obj.create(**data)

            response.code = 200
            response.msg = '测试通过'
            response.data ={}
            if flag:
                response.code = 301
                response.msg = '测试失败'
                response.data = result_data

        else:
            response.code = 301
            response.msg = '参数错误'
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)

