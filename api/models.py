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
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户", related_name='userprofile_self', null=True, blank=True)

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    status_choices = (
        (1, '启用'),
        (2, '不启用'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)

    role = models.ForeignKey('role', verbose_name='所属角色', null=True, blank=True)
    company = models.ForeignKey('company', verbose_name='所属公司', null=True, blank=True)      # 超级管理员没有所属公司
    set_avator = models.CharField(verbose_name='头像', default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg', max_length=128)

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
        (2, '等待评估'),
        (3, '等待开发'),
        (4, '等待测试'),
        (5, '待上线'),
        (6, '开发完成'),
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
    img_list = models.TextField(verbose_name="进展图片", null=True, blank=True)    # 测试结果中需要用到
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('userprofile', verbose_name='创建需求日志的用户')

# 测试用例接口分组
class caseInterfaceGrouping(models.Model):
    talkProject = models.ForeignKey(to='project', verbose_name="所属产品项目", null=True, blank=True)
    operUser = models.ForeignKey(to='userprofile', verbose_name="创建用户", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    parensGroupName = models.ForeignKey(to='self', verbose_name='父级分组', null=True, blank=True)
    groupName = models.CharField(verbose_name='分组名称', max_length=64)
    level = models.IntegerField(verbose_name='分类等级', default=1)

# 测试用例接口详情
class caseInterfaceDetaile(models.Model):
    ownershipGroup = models.ForeignKey(to='caseInterfaceGrouping',verbose_name='分组', null=True, blank=True)
    hostManage = models.ForeignKey(to='configurationManagementHOST',verbose_name='host配置管理', null=True, blank=True)
    url = models.TextField(verbose_name='url', null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    status_choices = (
        (1,'GET'),
        (2,'POST')
    )
    requestType = models.SmallIntegerField(verbose_name='请求类型', choices=status_choices, default=1)
    caseName = models.CharField(verbose_name='接口名称', max_length=64)
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='创建人')
    getRequestParameters = models.TextField(verbose_name='GET请求参数', null=True, blank=True)
    postRequestParameters = models.TextField(verbose_name='POST请求参数', null=True, blank=True)


# HOST 管理配置
class configurationManagementHOST(models.Model):
    hostName = models.CharField(verbose_name='host名字', max_length=128)
    hostUrl = models.CharField(verbose_name='hostUrl', max_length=128)
    userProfile = models.ForeignKey(to='userprofile', null=True, blank=True, verbose_name='创建人')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    status_choices = (
        (1, '测试环境'),
        (2, '正式环境')
    )
    describe = models.SmallIntegerField(verbose_name='描述', choices=status_choices, default=1)


