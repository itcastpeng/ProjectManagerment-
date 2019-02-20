from django.db import models


# Create your models here.


# 公司表
class company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户", related_name='company_userprofile')


# 角色表
class role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户", related_name='role_user')
    permissions = models.ManyToManyField('permissions', verbose_name="拥有权限")


# 权限表
class permissions(models.Model):
    name = models.CharField(verbose_name="权限名称", max_length=128)
    title = models.CharField(verbose_name="权限标题", max_length=128)
    pid = models.ForeignKey('self', verbose_name="父级权限", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户", related_name='permissions_user')


# 用户表
class userprofile(models.Model):
    username = models.CharField(verbose_name="用户账号", max_length=128)
    password = models.CharField(verbose_name="用户密码", max_length=128)
    token = models.CharField(verbose_name="token值", max_length=128)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户", related_name='userprofile_self', null=True,
                                  blank=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    status_choices = (
        (1, '启用'),
        (2, '不启用'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)

    role = models.ForeignKey('role', verbose_name='所属角色', null=True, blank=True)
    company = models.ForeignKey('company', verbose_name='所属公司', null=True, blank=True)  # 超级管理员没有所属公司
    set_avator = models.CharField(verbose_name='头像', default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg',
                                  max_length=128)

    userid = models.CharField(verbose_name="企业微信id", max_length=64, null=True, blank=True)


# 产品项目表
class project(models.Model):
    status_choices = (
        (1, '正式环境'),
        (2, '灰度环境'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    is_switch = models.BooleanField(verbose_name="是否允许切换环境", default=False)

    name = models.CharField(verbose_name="项目名称", max_length=128)
    company = models.ForeignKey('company', verbose_name='所属公司')
    principal = models.ManyToManyField('userprofile', verbose_name='负责人', related_name='principal_userprofile')
    developer = models.ManyToManyField('userprofile', verbose_name='开发人员', related_name='developer_userprofile')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户")


# 产品功能表
class action(models.Model):
    name = models.CharField(verbose_name="功能名称", max_length=128)
    project = models.ForeignKey('project', verbose_name="所属产品项目")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户")


# 产品需求表
class demand(models.Model):
    action = models.ForeignKey('action', verbose_name='所属功能')
    project = models.ForeignKey('project', verbose_name="所属产品项目")
    name = models.CharField(verbose_name="需求名称", max_length=128)
    remark = models.TextField(verbose_name="需求描述")
    img_list = models.TextField(verbose_name="需求图片", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    complete_date = models.DateTimeField(verbose_name="预计完成时间", null=True, blank=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建需求的用户")
    # developer = models.ManyToManyField('userprofile', verbose_name='开发人员', related_name='demand_developer_userprofile')

    status_choices = (
        (1, '等待审核'),
        (7, '提交BUG'),
        (2, '等待评估'),
        (3, '等待开发'),
        (4, '等待测试'),
        (5, '待上线'),
        (6, '开发完成'),
        (8, '驳回,待评估'),
        # (10, '上线成功'),
        (11, '关闭需求'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)

    urgency_level_choices = (
        (1, "普通"),
        (2, "紧急"),
        (3, "很紧急"),
        (4, "非常紧急"),
    )
    urgency_level = models.SmallIntegerField(verbose_name="紧急程度", default=1, choices=urgency_level_choices)


# 产品需求表和用户管理第三张表
class demand_to_userprofile(models.Model):
    developer = models.ForeignKey('userprofile', verbose_name="开发人员表")
    demand = models.ForeignKey('demand', verbose_name='需求表')


# 需求进展表
class progress(models.Model):
    demand = models.ForeignKey('demand', verbose_name="需求名称")
    description = models.TextField(verbose_name="描述", null=True, blank=True)
    remark = models.TextField(verbose_name="备注信息", null=True, blank=True)
    img_list = models.TextField(verbose_name="进展图片", null=True, blank=True)  # 测试结果中需要用到
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('userprofile', verbose_name='创建需求日志的用户')


# ----------------------------------------测试用例------------------------------------------------

# 测试用例项目表
class caseInterProject(models.Model):
    name = models.CharField(verbose_name="项目名称", max_length=128)
    front_developer = models.ManyToManyField('userprofile', verbose_name='前端开发人员',
        related_name='userprofile_front_developer')
    back_developer = models.ManyToManyField('userprofile', verbose_name='后端开发人员',
        related_name='userprofile_back_developer')

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户")
    language_type_choices = (
        (1, 'python'),
        (2, 'php')
    )
    # 区分请求结果
    language_type = models.SmallIntegerField(verbose_name='语言类型', choices=language_type_choices, default=1)


# 测试用例接口分组
class caseInterfaceGrouping(models.Model):
    talk_project = models.ForeignKey(to='caseInterProject', verbose_name="所属项目", null=True, blank=True)
    operUser = models.ForeignKey(to='userprofile', verbose_name="创建用户", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    parensGroupName = models.ForeignKey(to='self', verbose_name='父级分组', null=True, blank=True)
    groupName = models.CharField(verbose_name='分组名称', max_length=64)
    level = models.IntegerField(verbose_name='分类等级', default=1)


# 测试用例接口详情
class caseInterfaceDetaile(models.Model):
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='创建人')
    ownershipGroup = models.ForeignKey(to='caseInterfaceGrouping', verbose_name='分组', null=True, blank=True)
    caseName = models.CharField(verbose_name='接口名称', max_length=64)  # 接口名字 (别名)
    hostManage = models.ForeignKey(to='configurationManagementHOST', verbose_name='host配置管理', null=True, blank=True)

    url = models.TextField(verbose_name='url', null=True, blank=True)
    getRequestParameters = models.TextField(verbose_name='GET请求参数', null=True, blank=True)
    postRequestParameters = models.TextField(verbose_name='POST请求参数', null=True, blank=True)

    status_choices = (
        (1, 'GET'),
        (2, 'POST'),
    )
    requestType = models.SmallIntegerField(verbose_name='请求类型', choices=status_choices, null=True, blank=True)
    xieyi_type_choices = (
        (1, 'http'),
        (2, 'https'),
    )
    xieyi_type = models.SmallIntegerField(verbose_name='协议', choices=xieyi_type_choices, null=True, blank=True)
    type_status_choices = (
        (1, '增加'),
        (2, '修改'),
        (3, '查询'),
        (4, '删除'),
    )
    type_status = models.IntegerField(verbose_name='接口类型', default=4, choices=type_status_choices)
    testCase = models.IntegerField(verbose_name='添加ID', null=True, blank=True)


# # HOST管理配置
class configurationManagementHOST(models.Model):
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='创建人')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    hostUrl = models.CharField(verbose_name='hostUrl', max_length=128)
    status_choices = (
        (1, '测试环境'),
        (2, '正式环境')
    )
    describe = models.SmallIntegerField(verbose_name='描述', choices=status_choices, default=1)
    talk_project = models.ForeignKey(to='caseInterProject', verbose_name="所属产品项目", null=True, blank=True)


# 请求结果保存 (历史请求)
class requestResultSave(models.Model):
    case_inter = models.ForeignKey(to='caseInterfaceDetaile', verbose_name='测试用例', null=True, blank=True)
    url = models.CharField(verbose_name='请求url', max_length=256, null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    result_data = models.TextField(verbose_name='返回结果', null=True, blank=True)


# 测试用例请求文档
class requestDocumentDoc(models.Model):
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    getRequestParameters = models.TextField(verbose_name='GET请求参数', null=True, blank=True)
    postRequestParameters = models.TextField(verbose_name='POST请求参数', null=True, blank=True)
    url = models.TextField(verbose_name='url', null=True, blank=True)
    jiekou_name = models.CharField(verbose_name='接口名称', max_length=64, null=True, blank=True)
    talk_project = models.ForeignKey(to='caseInterProject', verbose_name="所属产品项目", null=True, blank=True)
    interDetaile = models.ForeignKey(to='caseInterfaceDetaile', verbose_name="所属测试用例", null=True, blank=True)
    status_choices = (
        (1, 'GET'),
        (2, 'POST'),
    )
    requestType = models.SmallIntegerField(verbose_name='请求类型', choices=status_choices, null=True, blank=True)
    result_data = models.TextField(verbose_name='结果', null=True, blank=True)

# 请求文档定时刷新(请求完成后 定时刷新结果)
class requestDoc(models.Model):
    name = models.CharField(verbose_name='测试用例名称', max_length=64, null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    if_success = models.IntegerField(verbose_name='是否成功', null=True, blank=True)
    result_data = models.TextField(verbose_name='结果', null=True, blank=True)
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='创建人')


    is_automatic_test_choices = (
        (1, '自动测试'),
        (2, '手动测试')
    )
    is_automatic_test = models.SmallIntegerField(verbose_name='是否为机器测试', default=2)
    note = models.IntegerField(verbose_name='查询接口是否有日志', default=0)

# selenium自动测试文档
class selenium_test_doc(models.Model):
    title = models.CharField(verbose_name='测试名称', max_length=64)
    remak = models.CharField(verbose_name='备注', max_length=256, null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    if_success = models.IntegerField(verbose_name='是否成功', null=True, blank=True)    # 是否成功

# 自动测试(创建定时测试定时跑测试用例)
class timingCaseInter(models.Model):
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    case_inter_result = models.CharField(verbose_name='测试的分组', max_length=256)
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='操作人')
    run_time = models.DateTimeField(verbose_name='运行时间', null=True, blank=True)
    run_type_choises = (
        (1, '预计运行时间'),
        (2, '间隔时间运行')
    )
    run_type = models.SmallIntegerField(verbose_name='运行类型', choices=run_type_choises, default=1)
    expect_run_time = models.CharField(verbose_name='预计运行时间', max_length=128, null=True, blank=True)
    expect_time = models.CharField(verbose_name='时间段运行(多长时间执行一次)', max_length=128, null=True, blank=True)
    talk_project = models.ForeignKey(to='project', verbose_name='归属项目', null=True, blank=True)

# 实时查看api日志
class showApiLog(models.Model):
    name = models.CharField(verbose_name="项目名称", max_length=128)
    tgt = models.CharField(verbose_name="salt客户端key", max_length=128)
    logPath = models.CharField(verbose_name="日志绝对路径", max_length=256)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 所有人操作测试用例文档 日志
class operation_test_log(models.Model):
    casename = models.CharField(verbose_name='测试用例名称', max_length=128, null=True, blank=True)
    interface_type_choices = (
        (1, '增加'),
        (2, '修改'),
        (3, '删除')
    )
    interface_type = models.SmallIntegerField(verbose_name='接口类型', choices=interface_type_choices, default=1)
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='操作人')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# ------------------------------------------------------------------------------------------------------------------
