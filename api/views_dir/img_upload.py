import os
from django import forms
from publicFunc import Response
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import base64
from api import models
from publicFunc import account
import time


# 添加企业的产品
class imgUploadForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "图片名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    img_data = forms.CharField(
        error_messages={
            'required': "图片内容不能为空"
        }
    )

    chunk = forms.IntegerField(
        error_messages={
            'required': "当前是第几份文件不能为空",
            'invalid': '份数必须是整数类型'
        }
    )

    img_source =  forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid':  "必须是字符串"
        }
    )


# 上传图片（分片上传）
@csrf_exempt
@account.is_token(models.userprofile)
def img_upload(request):
    response = Response.ResponseObj()

    forms_obj = imgUploadForm(request.POST)
    if forms_obj.is_valid():

        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
        chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
        expanded_name = img_name.split('.')[-1]  # 扩展名

        img_name = timestamp + "_" + str(chunk) + '.' + expanded_name
        img_save_path = os.path.join('statics', 'imgs', img_name)
        print('img_save_path -->', img_save_path )

        with open(img_save_path, 'w') as f:
            f.write(img_data)

        response.code = 200
        response.msg = "上传成功"

    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 合并图片 Form 验证
class imgMergeForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "文件名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    chunk_num = forms.IntegerField(
        error_messages={
            'required': "总份数不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )
    img_source = forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid':  "必须是字符串"
        }
    )


# 合并图片
@csrf_exempt
@account.is_token(models.userprofile)
def img_merge(request):
    response = Response.ResponseObj()
    forms_obj = imgMergeForm(request.POST)
    if forms_obj.is_valid():
        img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
        timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
        chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
        expanded_name = img_name.split('.')[-1]  # 扩展名
        picture_type = request.POST.get('picture_type')  # 图片的类型  (1, '产品封面的图片'), (2, '产品介绍的图片')
        img_name = timestamp + '.' + expanded_name
        img_source = forms_obj.cleaned_data.get('img_source')  # user_photo 代表用户上传的照片  user_avtor 代表用户的头像。
        print('-----img_source----->', img_source)

        file_dir = os.path.join('statics', 'imgs')

        fileData = ''
        for chunk in range(chunk_num):
            file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            file_save_path = os.path.join('statics', 'imgs', file_name)
            with open(file_save_path, 'r') as f:
                fileData += f.read()

            os.remove(file_save_path)

        # user_id = request.GET.get('user_id')
        img_path = os.path.join(file_dir, img_name)
        # img_save_path = os.path.join(BasePath, img_path)
        file_obj = open(img_path, 'ab')
        img_data = base64.b64decode(fileData)
        file_obj.write(img_data)
        # obj = models.zgld_user_photo.objects.create(user_id=user_id, photo_url=img_path,photo_type=2)   # 用户名片头像

        response.data = {
            'picture_url': img_path,
        }
        response.code = 200
        response.msg = "添加图片成功"

    else:
        response.code = 303
        response.msg = "上传异常"
        response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 图片上传
@csrf_exempt
def ueditor_image_upload(request):

    # action为config 从服务器返回配置
    # https://github.com/bffor/python-ueditor
    # http://127.0.0.1:8001/zhugeleida/public/ueditor_img_upload?action=config
    if request.GET.get('action') == 'config':
        '''
        为uploadimage 上传图片 对图片进行处理
        config.json 配置文件 详细设置参考：http://fex.baidu.com/ueditor/#server-deploy
        '''

        # f = open('config.json', encoding='utf-8')
        # data = f.read()
        # f.close()
        # temp = json.loads(data)
        # callbackname = request.GET.get('callback')
        # # 防止XSS 过滤  callbackname只需要字母数字下划线
        # pattern = re.compile('\w+', re.U)
        # matchObj = re.findall(pattern, callbackname, flags=0)
        # callbacks = matchObj[0] + '(' + json.dumps(temp) + ')'
        # return HttpResponse(callbacks)
        from api.views_dir.UEditorUploadConfig import UEditorUploadSettings
        if "callback" not in request.GET:
            return JsonResponse(UEditorUploadSettings)
        else:
            return_str = "{0}({1})".format(request.GET["callback"], json.dumps(UEditorUploadSettings, ensure_ascii=False))
            print('====')
            print('return_str -->', return_str)
            return HttpResponse(return_str)
    elif request.GET.get('action') == 'uploadimage':
        img = request.FILES.get('upfile')
        name = request.FILES.get('upfile').name

        print('------request.FILES-------->>',request.FILES.get,img,name)

        allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp']
        # file_suffix = name.split(".")[-1]
        file_suffix = name.split(".")[-1]

        if file_suffix not in allow_suffix:
            return {"state": 'error', "name": name, "url": "", "size": "", "type": file_suffix}

        # 上传文件路径
        dir_name = os.path.join('statics', 'imgs')

        file_name = str(int(time.time() * 1000)) + "." + file_suffix

        filenameurl = os.path.join(dir_name, file_name)
        print('filenameurl -->', filenameurl)
        with open(filenameurl, 'wb+') as destination:
            for chunk in img.chunks():
                destination.write(chunk)
        data = {"state": 'SUCCESS', "url": '/' + filenameurl, "title": file_name, "original": name, "type": file_suffix}

        print('-------data-------->>',data)

        return JsonResponse(data)