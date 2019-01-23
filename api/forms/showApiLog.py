from django import forms

from api import models
from publicFunc import account
import time


# 实时获取日志
class ShowLogForm(forms.Form):
    lineNum = forms.IntegerField(
        required=True,
        error_messages={
            'required': "日志开始行号不能为空"
        }
    )

    filterKeyWorld = forms.CharField(
        required=False,
    )
