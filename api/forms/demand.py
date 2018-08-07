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

    project_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "项目名称不能为空"
        }
    )

    action_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "功能名称不能为空"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "需求名称不能为空"
        }
    )

    remark = forms.CharField(
        required=True,
        error_messages={
            'required': "需求描述不能为空"
        }
    )

    img_list = forms.CharField(
        required=False
    )

    urgency_level = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择紧急程度"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']
        project_id = self.data['project_id']
        action_id = self.data['action_id']
        objs = models.demand.objects.filter(
            name=name,
            project_id=project_id,
            action_id=action_id
        )
        if objs:
            self.add_error('name', '功能名称已存在')
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

    project_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "项目名称不能为空"
        }
    )

    action_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "功能名称不能为空"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "需求名称不能为空"
        }
    )

    remark = forms.CharField(
        required=True,
        error_messages={
            'required': "需求描述不能为空"
        }
    )

    img_list = forms.CharField(
        required=False
    )

    urgency_level = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择紧急程度"
        }
    )

    # 判断名称是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['name']
        project_id = self.data['project_id']
        action_id = self.data['action_id']

        objs = models.demand.objects.filter(
            name=name,
            project_id=project_id,
            action_id=action_id
        ).exclude(
            id=o_id,
        )
        if objs:
            self.add_error('name', '功能名称已存在')
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


# 审核
class ShenHeForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '需求id不能为空'
        }
    )

    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    developerList = forms.CharField(
        required=False,
        error_messages={
            'required': "开发人员不能为空"
        }
    )

    remark = forms.CharField(
        required=False
    )

    img_list = forms.CharField(
        required=False
    )