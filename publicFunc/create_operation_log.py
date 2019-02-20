
from api import models


# 增加测试用例操作日志
def create_operation_log(result_data):
    print(result_data)
    models.operation_test_log.objects.create(**result_data)

