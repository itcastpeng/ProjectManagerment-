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
    language_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "语言类型不能为空"
        }
    )

    front_developer = forms.CharField(
        required=True,
        error_messages={
            'required': "前端开发人不能为空"
        }
    )
    back_developer = forms.CharField(
        required=True,
        error_messages={
            'required': "前端开发人不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.caseInterProject.objects.filter(
            name=name,
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
    front_developer = forms.CharField(
        required=True,
        error_messages={
            'required': "前端开发人不能为空"
        }
    )
    back_developer = forms.CharField(
        required=True,
        error_messages={
            'required': "前端开发人不能为空"
        }
    )

    # 判断名称是否存在
    # def clean_name(self):
    #     o_id = self.data['o_id']
    #     name = self.data['name']
    #     objs = models.caseInterProject.objects.filter(
    #         name=name,
    #     ).exclude(
    #         id=o_id,
    #     )
    #     if objs:
    #         self.add_error('name', '项目名称已存在')
    #     else:
    #         return name

# 删除
class DeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '修改id不能为空'
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        host_obj = models.configurationManagementHOST.objects.filter(id=o_id)
        if not host_obj:
            group_obj = models.caseInterfaceGrouping.objects.filter(id=o_id)
            if not group_obj:
                objs = models.caseInterProject.objects.filter(id=o_id)
                if objs:
                    return o_id
                else:
                    self.add_error('o_id', '删除ID不存在')
            else:
                self.add_error('o_id', '含有子级, 请先移除')
        else:
            self.add_error('o_id', '含有子级, 请先移除')

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
