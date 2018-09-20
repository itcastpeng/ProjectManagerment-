from django import forms

from api import models
import json


# 添加
class AddForm(forms.Form):
    url = forms.CharField(
        required=True,
        error_messages={
            'required': "url不能为空"
        }
    )
    ownershipGroup_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '父级分组名称类型错误'
        }
    )

    def clean_ownershipGroup_id(self):
        ownershipGroup_id = self.data.get('ownershipGroup_id')
        objs = models.caseInterfaceGrouping.objects.filter(id=ownershipGroup_id)
        if not objs:
            self.add_error('ownershipGroup_id', '无此分组')
        else:
            return ownershipGroup_id
# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改ID不能为空"
        }
    )

    url = forms.CharField(
        required=True,
        error_messages={
            'required': "url不能为空"
        }
    )
    ownershipGroup_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '父级分组名称类型错误'
        }
    )

    def clean_ownershipGroup_id(self):
        ownershipGroup_id = self.data.get('ownershipGroup_id')
        objs = models.caseInterfaceGrouping.objects.filter(id=ownershipGroup_id)
        if not objs:
            self.add_error('ownershipGroup_id', '无此分组')
        else:
            return ownershipGroup_id
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.caseInterfaceDetaile.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '要修改分组ID有误')
        else:
            return o_id

    # 判断名称是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['name']
        objs = models.role.objects.filter(
            name=name,
        ).exclude(id=o_id)
        if objs:
            self.add_error('name', '角色名称已存在')
        else:
            return name

    def clean_permissionsList(self):
        permissionsList = self.data.get('permissionsList')
        return json.loads(permissionsList)

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