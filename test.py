









import re
#
# requestUrl = 'http://xmgl.zhugeyingxiao.com/api/testCaseGroup/update/6?user_id'
#
#
#
# get_canshu = requestUrl.split('?')[1]
#
# num = re.sub(r'\?.*$', "", requestUrl)
# canshu = num[num.rfind('/'):]
#
# print('canshu--> ', canshu)
#
testCase = 56
#
# requestUrl = requestUrl.replace(canshu.strip(), testCase)
#
# print('requestUrl--> ', requestUrl)


#
# requestUrl = 'http://127.0.0.1:8001/api/testCaseDetaile/update/55555?beforeTaskId=2&rand_str=f2dd5cd6544a39a82d437bfa1bf8216a&timestamp=1547013904167&user_id=7'
#
#
#
# num = re.sub(r'\?.*$', "", requestUrl)
# canshu = num[num.rfind('/'):]
# requestUrl = requestUrl.replace(canshu.strip(), '/' + str(testCase))
#
#
# print(requestUrl)




p = [{"key":"timestamp[]","value":"1545822031837","describe":""},{"key":"user_id","value":"1","describe":""},{"key":"rand_str","value":"7893210276cb01c39c073b2564edfb05","describe":""}]
for i in p:
    if '[]' in i['key']:
        print('=========')















