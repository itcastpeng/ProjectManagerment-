from django import forms

from api import models
import json

# 更新
class UpdateForm(forms.Form):
    newPwd = forms.CharField(
        required=True,
        error_messages={
            'required': '原始密码不能为空'
        }
    )
    oldPwd = forms.CharField(
        required=True,
        error_messages={
            'required': '新密码不能为空'
        }
    )

