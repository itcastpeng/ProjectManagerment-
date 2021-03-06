from django import forms

from api import models
from publicFunc import account
import time


# 添加
class AddForm(forms.Form):
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "项目名称不能为空"
        }
    )
    principalList = forms.CharField(
        required=True,
        error_messages={
            'required': "项目负责人不能为空"
        }
    )

    developerList = forms.CharField(
        required=True,
        error_messages={
            'required': "项目负责人不能为空"
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司名称不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']
        company_id = self.data['company_id']
        objs = models.project.objects.filter(
            name=name,
            company_id=company_id,
        )
        if objs:
            self.add_error('name', '项目名称已存在')
        else:
            return name


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色id不能为空'
        }
    )
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "项目名称不能为空"
        }
    )
    principalList = forms.CharField(
        required=True,
        error_messages={
            'required': "项目负责人不能为空"
        }
    )

    developerList = forms.CharField(
        required=True,
        error_messages={
            'required': "项目负责人不能为空"
        }
    )

    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司名称不能为空"
        }
    )

    # 判断名称是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['name']
        company_id = self.data['company_id']
        objs = models.project.objects.filter(
            name=name,
            company_id=company_id
        ).exclude(
            id=o_id,
        )
        if objs:
            self.add_error('name', '项目名称已存在')
        else:
            return name


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
    company_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "公司ID不能为空"
        }
    )

    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "角色ID不能为空"
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
