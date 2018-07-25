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


# 用户表
class userprofile(models.Model):
    username = models.CharField(verbose_name="用户账号", max_length=128)
    password = models.CharField(verbose_name="用户密码", max_length=128)
    token = models.CharField(verbose_name="token值", max_length=128)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建用户", related_name='userprofile_self')

    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    status_choices = (
        (1, '启用'),
        (2, '不启用'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)

    role = models.ForeignKey('role', verbose_name='所属角色')
    company = models.ForeignKey('company', verbose_name='所属公司', null=True, blank=True)      # 超级管理员没有所属公司
    set_avator = models.CharField(verbose_name='头像', default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg', max_length=128)


# 产品项目表
class project(models.Model):
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
    remark = models.TextField(verbose_name="需求描述", max_length=128)
    img_list = models.TextField(verbose_name="需求图片", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    complete_date = models.DateTimeField(verbose_name="预计完成时间", null=True, blank=True)
    oper_user = models.ForeignKey('userprofile', verbose_name="创建需求的用户")

    status_choices = (
        (1, '审核中'),
        (2, '开发中'),
        (3, '测试中'),
        (4, '已完成'),
        (10, '已关闭'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)

    urgency_level_choices = (
        (1, "普通"),
        (2, "紧急"),
        (3, "很紧急"),
        (4, "非常紧急"),
    )
    urgency_level = models.SmallIntegerField(verbose_name="紧急程度", default=1, choices=urgency_level_choices)


# 需求进展表
class progress(models.Model):
    demand = models.ForeignKey('demand', verbose_name="需求名称")
    description = models.TextField(verbose_name="进展描述")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('userprofile', verbose_name='创建需求日志的用户')
