from django.db import models

# Create your models here.


# 公司表
class company(models.Model):
    name = models.CharField(verbose_name="公司名称", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 部门表
class department(models.Model):
    name = models.CharField(verbose_name="部门名称", max_length=128)
    company = models.ForeignKey('company', verbose_name='所属公司')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 角色表
class role(models.Model):
    name = models.CharField(verbose_name="角色名称", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 用户表
class userprofile(models.Model):
    username = models.CharField(verbose_name="用户账号", max_length=128)
    password = models.CharField(verbose_name="用户密码", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    status_choices = (
        (1, '启用'),
        (2, '不启用'),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)

    role = models.ForeignKey('role', verbose_name='所属角色')
    department = models.ForeignKey('department', verbose_name='所属部门')


# 产品项目表
class project(models.Model):
    name = models.CharField(verbose_name="项目名称", max_length=128)
    principal = models.ManyToManyField('userprofile', verbose_name='负责人', related_name='principal_userprofile')
    developer = models.ManyToManyField('userprofile', verbose_name='开发人员', related_name='developer_userprofile')
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 产品功能表
class action(models.Model):
    name = models.CharField(verbose_name="项目名称", max_length=128)
    project = models.ForeignKey('project', verbose_name="所属产品项目")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 产品需求表
class demand(models.Model):
    action = models.ForeignKey('action', verbose_name='所属功能')
    name = models.CharField(verbose_name="需求名称", max_length=128)
    remark = models.TextField(verbose_name="需求描述", max_length=128)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('userprofile', verbose_name='创建需求的用户')

    status_choices = (
        (1, '开发中'),
        (2, '开发中'),
    )


# 需求进展表
class progress(models.Model):
    demand = models.ForeignKey('demand', verbose_name="需求名称")
    description = models.TextField(verbose_name="进展描述")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('userprofile', verbose_name='创建需求日志的用户')
