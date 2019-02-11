import requests


class gitlabApi:
    def __init__(self):
        self.private_token = "Wuu2WEjzT-z6x9xsJyQL"
        self.projects_data = {}     # 所有项目数据

    # 获取所有项目
    def get_projects(self):
        url = "http://gitlab.zhugeyingxiao.com/api/v4/projects"
        params = {
            'per_page': 1000,
            'private_token': self.private_token,
            # 'simple': True,
            'owned': True,
            # 'order_by': 'id',
            # 'sort': 'asc'
        }

        ret = requests.get(url, params=params)
        for i in ret.json():
            self.projects_data[i['id']] = i['name']
            # print(i['name'], i['id'])
            # print(i)
        # print(self.projects_data)
        # print('-' * 100)

    # 查询未合并的请求
    def merge_requests(self):
        url = 'http://gitlab.zhugeyingxiao.com/api/v4/merge_requests'

        params = {
            'private_token': self.private_token,
            "scope": "all",
            "state": "opened"
        }

        ret = requests.get(url, params=params)

        for item in ret.json():
            # print(item)
            projects_name = self.projects_data[item['project_id']]
            msg = "项目 [{projects_name}] 由 {name} 提交进行合并，合并备注：{title}".format(
                projects_name=projects_name,
                name=item['author']['name'],
                title=item['title'],
            )
            print(msg)

            project_id = item['project_id']
            merge_request_iid = item['iid']

            print('进行合并 ---->')
            self.merge_requests_accept(project_id, merge_request_iid)

            # print('查询是否合并成功')
            status = self.merge_requests_status(project_id, merge_request_iid)

            rename = "失败"
            if status:
                rename = "成功"

            msg = "项目 [{projects_name}] 合并 {rename} \n".format(
                projects_name=projects_name,
                rename=rename
            )

            print(msg)

    # 查询合并状态
    def merge_requests_status(self, project_id, merge_request_iid):
        """
        :param project_id:  项目id
        :param merge_request_iid: 合并请求的id
        :return:
        """
        params = {
            'private_token': self.private_token,
        }
        url = "http://gitlab.zhugeyingxiao.com/api/v4/projects/{id}/merge_requests/{merge_request_iid}".format(
            id=project_id,
            merge_request_iid=merge_request_iid
        )

        ret = requests.get(url, params=params)
        # print(ret.url)
        # print(ret.text)

        status = True
        if ret.json()['state'] == 'open':
            status = False

        return status

    # 合并代码
    def merge_requests_accept(self, project_id, merge_request_iid):

        params = {
            'private_token': 'Wuu2WEjzT-z6x9xsJyQL',
        }

        url = "http://gitlab.zhugeyingxiao.com/api/v4/projects/{project_id}/merge_requests/{merge_request_iid}/merge".format(
            project_id=project_id,
            merge_request_iid=merge_request_iid,
        )

        ret = requests.put(url, params=params)
        # print(ret.text)


if __name__ == '__main__':
    obj = gitlabApi()
    obj.get_projects()
    obj.merge_requests()
