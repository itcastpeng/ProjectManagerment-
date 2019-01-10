from django import forms

from api import models
import json


# 添加
class AddForm(forms.Form):
    # hostName = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': "域名名称不能为空"
    #     }
    # )
    hostUrl = forms.CharField(
        required=True,
        error_messages={
            'required': '域名URL不能为空'
        }
    )
    describe = forms.IntegerField(
        required=True,
        error_messages={
            'required': '描述不能为空'
        }
    )
    talk_project_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '所属产品项目不能为空'
        }
    )

    def clean_hostUrl(self):
        hostUrl = self.data.get('hostUrl')
        objs = models.configurationManagementHOST.objects.filter(hostUrl=hostUrl)
        if objs:
            self.add_error('hostUrl', 'HOST名称已存在')
        else:
            return hostUrl

# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改ID不能为空"
        }
    )
    hostUrl = forms.CharField(
        required=True,
        error_messages={
            'required': '域名URL不能为空'
        }
    )
    describe = forms.IntegerField(
        required=True,
        error_messages={
            'required': '描述不能为空'
        }
    )
    talk_project_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '所属产品项目不能为空'
        }
    )
    def clean_hostUrl(self):
        hostUrl = self.data.get('hostUrl')
        o_id = self.data.get('o_id')

        objs = models.configurationManagementHOST.objects.filter(hostUrl=hostUrl).exclude(id=o_id)
        if objs:
            self.add_error('hostUrl', 'HOST名称已存在')
        else:
            return hostUrl

# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length