
from django.conf.urls import url

from api.views_dir import login, company, role, user, project, action


urlpatterns = [
    url(r'^login$', login.login),

    # 公司管理
    url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    url(r'^company', company.company),

    # 角色管理
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),

    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # 产品管理
    url(r'^project/(?P<oper_type>\w+)/(?P<o_id>\d+)', project.project_oper),
    url(r'^project', project.project),

    # 功能管理
    url(r'^action/(?P<oper_type>\w+)/(?P<o_id>\d+)', action.action_oper),
    url(r'^action', action.action),

]
