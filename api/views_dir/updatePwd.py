from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from api.forms.updatePwd import UpdateForm
import json
#  增删改
#  csrf  token验证
@csrf_exempt
@account.is_token(models.userprofile)
def updatePassword(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')
        if oper_type == "update":
            if user_id:
                form_data = {
                    'newPwd': request.POST.get('newPwd'),
                    'oldPwd': request.POST.get('oldPwd')
                }
                userObjs = models.userprofile.objects.filter(id=user_id)
                forms_obj = UpdateForm(form_data)
                if userObjs:
                    if forms_obj.is_valid():
                        oldPwd = forms_obj.cleaned_data.get('oldPwd')
                        md5OldPwd = account.str_encrypt(oldPwd)
                        if md5OldPwd == userObjs[0].password:
                            md5NewPwd = account.str_encrypt(forms_obj.cleaned_data.get('newPwd'))
                            userObjs.update(password=md5NewPwd)
                            response.code = 200
                            response.msg = "修改成功"
                        else:
                            response.code = 402
                            response.msg = '原始密码错误,请重新输入！'
                    else:
                        print("验证不通过")
                        # print(forms_obj.errors)
                        response.code = 301
                        # print(forms_obj.errors.as_json())
                        response.msg = json.loads(forms_obj.errors.as_json())
                else:
                    response.code = 402
                    response.msg = '未查询到此用户！'
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)

















