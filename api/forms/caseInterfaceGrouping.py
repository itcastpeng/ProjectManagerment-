from django import forms

from api import models
import json


# 添加
class AddForm(forms.Form):
    groupName = forms.CharField(
        required=True,
        error_messages={
            'required': "分组名称不能为空"
        }
    )
    parensGroupName = forms.IntegerField(
        required=False,
        error_messages={
            'required': '父级分组名称类型错误'
        }
    )
    operUser_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作人不能为空"
        }
    )
    talk_project_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "归属项目不能为空"
        }
    )
    def clean_talk_project_id(self):
        talk_project_id = self.data.get('talk_project_id')
        objs = models.project.objects.filter(id=talk_project_id)
        if not objs:
            self.add_error('talk_project_id', '无此项目')
        else:
            return talk_project_id

# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改ID不能为空"
        }
    )
    groupName = forms.CharField(
        required=True,
        error_messages={
            'required': "分组名称不能为空"
        }
    )
    parensGroupName = forms.IntegerField(
        required=False,
        error_messages={
            'required': '父级分组名称类型错误'
        }
    )
    operUser_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作人不能为空"
        }
    )
    talk_project_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "归属项目不能为空"
        }
    )

    def clean_talkProject(self):
        talkProjectId = self.data.get('talkProject')
        objs = models.project.objects.filter(id=talkProjectId)
        if not objs:
            self.add_error('talkProject', '无此项目')

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.caseInterfaceGrouping.objects.filter(id=o_id)
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

# 删除
class DeleteForm(forms.Form):

    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "删除ID不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.caseInterfaceGrouping.objects.filter(id=o_id)
        if objs:
            if objs.filter(parensGroupName_id=o_id).count() > 0:
                self.add_error('o_id', '含有子级数据,请先删除或转移子级数据')
            else:
                detailObj = models.caseInterfaceDetaile.objects.filter(ownershipGroup_id=o_id)
                if detailObj:
                    self.add_error('o_id', '含有子级数据,请先删除或转移子级数据')
                else:
                    return o_id
        else:
            self.add_error('o_id', '权限不足')

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

