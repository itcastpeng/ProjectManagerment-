
import re

p = 'http://xmgl.zhugeyingxiao.com/api/testCaseGroup/update/6?user_id=10&rand_str=2be6ba2fa87950c7fb15c5c358722408&timestamp=1534157927644'





print()

zuo = p.split('?')[0]
you = p.split('?')[1]


requestUrl = zuo.replace(zuo.split('/')[-1], '+++')


print(requestUrl)


