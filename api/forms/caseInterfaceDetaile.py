from django import forms

from api import models
import json


# 添加
class AddForm(forms.Form):
    ownershipGroup_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '父级分组名称类型错误'
        }
    )

    hostManage_id = forms.IntegerField(
            required=False,
            error_messages={
                'required': '域名类型错误'
            }
        )
    # requestType  = forms.IntegerField(
    #         required=False,
    #         error_messages={
    #             'required': '请求类型类型错误'
    #         }
    #     )
    caseName = forms.CharField(
            required=True,
            error_messages={
                'required': '接口名称类型错误'
            }
        )
    type_status = forms.IntegerField(
            required=True,
            error_messages={
                'required': '接口类型类型错误'
            }
        )
    # xieyi_type = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '协议类型类型错误'
    #     }
    # )

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

    ownershipGroup_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '父级分组名称类型错误'
        }
    )

    hostManage_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '域名类型错误'
        }
    )
    requestType = forms.IntegerField(
        required=True,
        error_messages={
            'required': '请求类型不能为空'
        }
    )
    caseName = forms.CharField(
        required=True,
        error_messages={
            'required': '接口名称不能为空'
        }
    )
    type_status = forms.IntegerField(
        required=True,
        error_messages={
            'required': '接口类型不能为空'
        }
    )
    xieyi_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': '协议类型不能为空'
        }
    )
    requestUrl = forms.CharField(
        required=True,
        error_messages={
            'required': 'URL不能为空'
        }
    )
    getRequest = forms.CharField(
        required=True,
        error_messages={
            'required': 'GET参数类型错误'
        }
    )
    postRequest = forms.CharField(
        required=True,
        error_messages={
            'required': 'POST参数类型错误'
        }
    )

    def clean_hostManage_id(self):
        hostManage_id = self.data.get('hostManage_id')
        objs = models.configurationManagementHOST.objects.filter(id=hostManage_id)
        if objs:
            hostUrl = objs[0].hostUrl
            return hostManage_id, hostUrl
        else:
            self.add_error('hostManage_id', '权限不足')

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
            self.add_error('o_id', '权限不足')
        else:
            return o_id

    # 判断名称是否存在
    def clean_caseName(self):
        o_id = self.data['o_id']
        caseName = self.data['caseName']
        objs = models.caseInterfaceDetaile.objects.filter(
            caseName=caseName,
        ).exclude(id=o_id)
        if objs:
            self.add_error('caseName', '接口名称已存在')
        else:
            return caseName


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
        objs = models.caseInterfaceDetaile.objects.filter(id=o_id)
        if objs:
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


# 添加自动测试
class AddTimingCase(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "操作人不能为空"
        }
    )
    case_inter_result = forms.CharField(
        required=True,
        error_messages={
            'required': "要运行的分组ID列表不能为空"
        }
    )
    run_type =forms.IntegerField(
        required=True,
        error_messages={
            'required':'运行类型不能为空'
        }
    )
    expect_run_time = forms.CharField(
        required=False,
        error_messages={
            'required': '预计运行时间类型错误'
        }
    )
    expect_time = forms.CharField(
        required=False,
        error_messages={
            'required': '时间段运行时(多久运行一次)不能为空'
        }
    )

    def clean_run_type(self):
        run_type = self.data.get('run_type')
        expect_run_time = self.data.get('expect_run_time')
        expect_time = self.data.get('expect_time')
        if int(run_type) == 1 and not expect_run_time:
            self.add_error('run_type', '请选择预计运行时间')
        elif int(run_type) == 2 and not expect_time:
            self.add_error('run_type', '请选择时间段运行(分钟为单位)')
        else:
            if int(run_type) == 1:
                expect_time = ''
            else:
                expect_run_time = ''
            return run_type, expect_run_time, expect_time

    def clean_case_inter_result(self):
        case_inter_result = self.data.get('case_inter_result')
        user_id = self.data.get('user_id')
        print('user_id--> ', user_id)
        for i in json.loads(case_inter_result):
            obj = models.caseInterfaceGrouping.objects.filter(id=i, operUser_id=user_id)
            if not obj:
                self.add_error('case_inter_result', '请选择正确分组')

        return json.loads(case_inter_result)

# 删除自动测试
class DeleteTimingCase(forms.Form):

    user_id = forms.CharField(
        required=True,
        error_messages={
            'required': "要运行的分组ID列表不能为空"
        }
    )
    o_id = forms.CharField(
        required=True,
        error_messages={
            'required': "要运行的分组ID列表不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        user_id = self.data.get('user_id')

        objs = models.timingCaseInter.objects.filter(id=o_id)
        if objs:
            if int(user_id) == int(objs[0].userProfile_id):
                return o_id
            else:
                self.add_error('o_id', '权限不足')
        else:
            self.add_error('o_id', '删除数据不存在')


