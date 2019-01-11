from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.document import SelectForm
import json
from django.db.models import Q

# cerf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def document(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'talk_project_id': '',
                'jiekou_name': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.requestDocumentDoc.objects.filter(q).order_by(order).order_by('create_date')
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                talk_project_name = ''
                talk_project_id = ''
                if obj.talk_project:
                    talk_project_name = obj.talk_project.name
                    talk_project_id = obj.talk_project_id
                print('obj.result_data--> ', obj.result_data , type(obj.result_data))
                ret_data.append({
                    'id': obj.id,

                    'getRequestParameters':json.loads(obj.getRequestParameters),        # GET  请求参数
                    'postRequestParameters':json.loads(obj.postRequestParameters),      # POST 请求参数
                    'url':obj.url,                                          # URL
                    'jiekou_name':obj.jiekou_name,                          # 接口名称
                    'requestType_id':obj.requestType,                       # 接口类型ID
                    'requestType':obj.get_requestType_display(),            # 接口类型

                    'talk_project_id':talk_project_id,                      # 项目ID
                    'talkProject': talk_project_name,                       # 项目名称

                    'result_data':json.loads(obj.result_data),              # 结果
                    'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })
            #  查询成功返回200状态码
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

