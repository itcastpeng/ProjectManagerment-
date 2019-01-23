#### code 说明：

```
200 正常

300 角色名已存在
301 数据类型验证失败
302 对应ID不存在
303 form 验证错误
304 含有子级数据,请先删除或转移子级数据
305 不允许删除自己
306 账户未启用

401 账号密码错误
402 请求方式异常 例如应该使用 POST 请求的使用的是 GET 请求
403 无任务
404 非法请求
```

####   公共参数（登录后所有api都需要加的参数）

``` python
请求方法：GET
请求参数:
参数名    是否必须    参数描述
rand_str    是        md5(timestamp + token) 使用 md5 进行加密
timestamp   是        时间戳   python获取方式: str(int(time.time() * 1000))   js 获取方式 new Date().getTime().toString(); 
user_id     是        当前登录用户ID

```

### 角色管理

#### 查询
```
http请求方式: GET
http请求url: http://192.168.10.240:8801/api/role

返回说明（正常时返回的json数据包示例）
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "ret_data": [
            {
                "id": 13,
                "name": "前端开发",
                "create_date": "2018-08-15 14:34:27",
                "oper_user__username": "张聪",
                "permissionsData": "[{\"title\": \"\\u516c\\u53f8\\u7ba1\\u7406\", \"expand\": true, \"id\": 10, \"checked\": false, \"children\": [{\"title\": \"\\u516c\\u53f8\\u7ba1\\u7406\", \"expand\": true, \"id\": 11, \"checked\": false}]}, {\"title\": \"\\u89d2\\u8272\\u7ba1\\u7406\", \"expand\": true, \"id\": 12, \"checked\": false, \"children\": [{\"title\": \"\\u89d2\\u8272\\u7ba1\\u7406\", \"expand\": true, \"id\": 13, \"checked\": false}]}, {\"title\": \"\\u6743\\u9650\\u7ba1\\u7406\", \"expand\": true, \"id\": 14, \"checked\": false, \"children\": [{\"title\": \"\\u6743\\u9650\\u7ba1\\u7406\", \"expand\": true, \"id\": 15, \"checked\": false}]}, {\"title\": \"\\u7528\\u6237\\u7ba1\\u7406\", \"expand\": true, \"id\": 16, \"checked\": false, \"children\": [{\"title\": \"\\u7528\\u6237\\u7ba1\\u7406\", \"expand\": true, \"id\": 17, \"checked\": false}]}, {\"title\": \"\\u9879\\u76ee\\u7ba1\\u7406\", \"expand\": true, \"id\": 18, \"checked\": false, \"children\": [{\"title\": \"\\u9879\\u76ee\\u7ba1\\u7406\", \"expand\": true, \"id\": 19, \"checked\": false}]}, {\"title\": \"\\u529f\\u80fd\\u7ba1\\u7406\", \"expand\": true, \"id\": 20, \"checked\": true, \"children\": [{\"title\": \"\\u529f\\u80fd\\u7ba1\\u7406\", \"expand\": true, \"id\": 21, \"checked\": false}]}, {\"title\": \"\\u9700\\u6c42\\u7ba1\\u7406\", \"expand\": true, \"id\": 22, \"checked\": true, \"children\": [{\"title\": \"\\u9700\\u6c42\\u7ba1\\u7406\", \"expand\": true, \"id\": 23, \"checked\": false}]}]"
                
                # 说明
                id                      角色id
                name                    角色名称
                create_date             创建时间
                oper_user__username     创建人，该角色是谁创建的
                permissionsData         该角色对应的权限,前端tree组件可以直接反序列化成数组之后直接使用
            }
        ],
        "data_count": 7
    }
}

```

#### 增加
```
http请求方式: POST
http请求url: http://192.168.10.240:8801/api/role/add/0        # 将角色ID修改为对应要操作的ID

POST 提交数据示例:
参数                              是否必传            描述
name                                yes              角色名称
permissionsList                     yes              角色具备权限列表的json格式字符串，例：[10,11,12,13]


返回说明（正常时返回的json数据包示例）
{
    "code": 200,
    "msg": "添加成功",
    "data": {}
}

```

#### 修改
```
http请求方式: POST
http请求url: http://192.168.10.240:8801/api/role/update/角色ID        # 将角色ID修改为对应要操作的ID

POST 提交数据示例:
参数                              是否必传            描述
name                                yes              角色名称
permissionsList                     yes              角色具备权限列表的json格式字符串，例：[10,11,12,13]


返回说明（正常时返回的json数据包示例）
{
    "code": 200,
    "msg": "修改成功",
    "data": {}
}

```

#### 删除
```
http请求方式: POST
http请求url: http://192.168.10.240:8801/api/role/delete/角色ID        # 将角色ID修改为对应要操作的ID

返回说明（正常时返回的json数据包示例）
{
    "code": 200,
    "msg": "删除成功",
    "data": {}
}

```

### 测试用例

#### 测试用例 分组 添加：
``` 
http请求： POST
http请求url：http://127.0.0.1:8000/api/testCaseGroupOper/add/0?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
groupName           POST                是                 分组名称
parensGroupName     POST                否                 父级分组ID
talkProject         POST                是                 归属项目

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "添加成功",
    "data": {}
}
```

#### 测试用例 分组 修改：
``` 
http请求： POST
http请求url：http://127.0.0.1:8000/api/testCaseGroupOper/update/6?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
groupName           POST                是                 分组名称
parensGroupName     POST                否                 父级分组ID
talkProject         POST                是                 归属项目

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "修改成功",
    "data": {}
}
```

#### 测试用例 分组 删除：
``` 
http请求： GET
http请求url：http://127.0.0.1:8000/api/testCaseGroupOper/delete/40?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
o_id                URL                 是                 要删除的分组ID
groupName           POST                是                 分组名称
parensGroupName     POST                否                 父级分组ID
talkProject         POST                是                 归属项目

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "删除成功",
    "data": {}
}
```

#### 测试用例 分组 查询：
``` 
http请求： GET
http请求url：http://127.0.0.1:8000/api/testCaseGroupOper/delete/40?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
o_id                URL                 是                 要删除的分组ID
groupName           POST                是                 分组名称
parensGroupName     POST                否                 父级分组ID
talkProject         POST                是                 归属项目

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "ret_data": [
            {
                "id": 1,                        ID
                "groupName": "第一个分组",       分组名称
                "parensGroupName_id": "",       父级为空 为顶级
                "parensGroupName": "",          父级名字
                "operUser": "赵欣鹏",            操作人
                "operUser_id": 10,              操作人ID
                "talkProject_id": 1,            项目ID
                "talkProject": "诸葛雷达"        项目名字
            },      
            {
                "id": 2,                        ID
                "groupName": "第一个分组",        分组名称  
                "parensGroupName_id": 1,        父级ID
                "parensGroupName": "第一个分组",  父级名字
                "operUser": "赵欣鹏",            操作人
                "operUser_id": 10,              操作人ID
                "talkProject_id": 1,            项目ID
                "talkProject": "诸葛雷达"        项目名称
            }
        ],
        "data_count": 2                         总数       
    }
}
```


#### 测试用例 详情 添加：
``` 
http请求： POST
http请求url：http://127.0.0.1:8000/api/testCaseGroupOper/delete/40?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
url                   POST                是                 url
ownershipGroup_id     POST                是                 分组ID
caseName              POST                是                 接口名称
requestType           POST                是                 请求类型
hostManage_id         POST                否                 域名
返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "添加成功",
    "data": {}
}

发送   POST 请求
requestType         GET                  是                 类型 GET or POST 
requestUrl          GET                  是                 请求 URL
getRequest          GET                  是                 客户 GET参数
postRequest         GET                  是                 客户 POST参数

add                 GET                  否                 如果是添加 加这个参数
caseName
hostManage_id
ownershipGroup_id
```

#### 测试用例 详情 修改：
``` 
http请求： POST
http请求url：http://127.0.0.1:8000/api/testCaseDetaileOper/update/1?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
url                   POST                是                 url
ownershipGroup_id     POST                是                 分组ID
caseName              POST                是                 接口名称
requestType           POST                是                 请求类型
hostManage_id         POST                否                 域名

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "修改成功",
    "data": {}
}
```

#### 测试用例 详情 删除：
``` 
http请求： POST
http请求url：http://127.0.0.1:8000/api/testCaseDetaileOper/update/1?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
o_id                GET                 是                  要删除的详情ID
返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "删除成功",
    "data": {}
}
```

#### 测试用例 详情 查询：
``` 
http请求： GET
http请求url： http://127.0.0.1:8000/api/testCaseDetaileShow?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644&beforeTaskId=3
返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "ret_data": [
            {
                "id": 12,                                   
                "ownershipGroup": "2号",                     
                "url": "sadasd asdas dsad",
                "create_date": "2018-09-20 20:13:53",
                "user_id": 10,
                "username": "赵欣鹏",
                "requestType": "GET",
                "jieKouName": "撒大声地按时"
            }
        ],
        "data_count": 1
    }
}
```

#### 测试用例 分组查询全部公司名 
```http://127.0.0.1:8000/api/testCaseGroupOper/selectTalkName/0?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644```

#### 测试用例 分组查询全部分组父级
```http://127.0.0.1:8000/api/testCaseGroupOper/superGroupName/0?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644 ```


#### 测试用例 host管理配置 增加：
``` 
http请求： POST
http请求url： http://127.0.0.1:8000/api/configurationHostOper/add/0?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
hostName            POST                是                 host别名
hostUrl             POST                是                 hostURL
describe            POST                是                 描述

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "添加成功",
    "data": {}
}
```

#### 测试用例 host管理配置 修改：
``` 
http请求： POST
http请求url： http://127.0.0.1:8000/api/configurationHostOper/update/3?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
o_id                URL                 是                 要删除的hostID
hostName            POST                是                 host别名
hostUrl             POST                是                 hostURL
describe            POST                是                 描述        

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "修改成功",
    "data": {}
}
```

#### 测试用例 host管理配置 删除：
``` 
http请求： POST
http请求url： http://127.0.0.1:8000/api/configurationHostOper/delete/2?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
o_id                URL                 是                 要删除的hostID
hostName            POST                是                 host别名
hostUrl             POST                是                 hostURL

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "删除成功",
    "data": {}
}
```

#### 测试用例 host管理配置 查询：
``` 
http请求： GET
http请求url： http://127.0.0.1:8000/api/configurationHostShow?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "ret_data": [
            {
                "id": 5,
                "name": "111",
                "url": "222",
                "username": "张聪",
                "user_id": 7,
                "describe_id": 1,
                "describe": "测试环境",
                "create_date": "2018-09-20 20:10:58"
            },
            {
                "id": 6,
                "name": "111",
                "url": "111",
                "username": "张聪",
                "user_id": 7,
                "describe_id": 1,
                "describe": "测试环境",
                "create_date": "2018-09-20 20:14:57"
            },
            {
                "id": 7,
                "name": "6565",
                "url": "6+26+",
                "username": "赵欣鹏",
                "user_id": 10,
                "describe_id": 1,
                "describe": "测试环境",
                "create_date": "2018-09-20 20:15:38"
            },
            {
                "id": 8,
                "name": "暗室逢灯",
                "url": "阿萨德",
                "username": "赵欣鹏",
                "user_id": 10,
                "describe_id": 2,
                "describe": "正式环境",
                "create_date": "2018-09-20 20:47:18"
            }
        ],
        "data_count": 4
    }
}
```

#### 查看api日志 - 获取项目名称
``` 
http请求： GET
http请求url： http://127.0.0.1:8801/api/show_api_log?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明

返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "ret_data": [
            {
                "id": 1,                            # 要查看日志的项目id
                "name": "项目管理平台"              # 要查看日志的项目名称
            }
        ]
    }
}
```


#### 查看api日志 - 获取实时日志
``` 
http请求： GET
http请求url： http://127.0.0.1:8801/api/show_api_log/showLog/:ID?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数   				请求方式		        是否必须            说明
:ID                 URL参数                   是               项目ID
lineNum             GET                       是               获取日志的最后行数，首次传0
filterKeyWorld      GET                       否                 匹配过滤条件，非必传


返回说明 （正常时返回的json数据 示例）
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "lineNum": 10,                      # 下次获取日志要提交的行号
        "logData": "10fdsafdafdas"          # 本次获取到的日志
    }
}
```












