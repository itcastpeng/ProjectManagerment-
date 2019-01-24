

## 自动测试

#### 自动测试 添加
```
http请求：POST
http请求url：http://127.0.0.1:8001/api/testCaseDetaile/add_timing_case/0?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数                      请求方式           必须                     说明
case_inter_result           POST            是                       分组ID 默认[] 多选
run_type                    POST            是                       运行类型
expect_run_time             POST            是                       预计运行时间(每天几点执行)
expect_time                 POST            是                       时间段运行(多久执行一次)

返回说明 （正常时返回的json数据 示例）
{
    "data": {
        "testCase": 3
    },
    "code": 200,
    "msg": "添加成功"
}
```

#### 自动测试 删除
```
http请求：POST
http请求url：http://127.0.0.1:8001/api/testCaseDetaile/delete_timing_case/4?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
参数                      请求方式           必须                     说明
o_id                    URL                 是                       要删除的自动测试ID


返回说明 （正常时返回的json数据 示例）
{
    "msg": "删除成功",
    "code": 200,
    "data": {}
}
```

#### 自动测试 查询
``` 
http请求：GET
http请求url：http://127.0.0.1:8001/api/testCaseDetaile/get_timing_case_result/4?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644
返回说明 （正常时返回的json数据 示例）
{
    "msg": "查询成功",
    "code": 200,
    "data": [
        {
            "expect_time": "",                          # 时间段运行(多久执行一次)
            "run_type_id": 1,                           # 运行时间类型 ID
            "expect_run_time": "9:30:00",               # 预计运行时间(每天几点执行)
            "create_date": "2019-01-15 11:14:07",       # 创建时间 
            "case_inter_result": [                      # 分组ID 数组格式
                37,
                49
            ],
            "run_type": "预计运行时间",                   # 运行类型 名称
            "run_time": "2019-01-16 11:14:10"           # 上次执行时间
        }        
    ]
}
```


