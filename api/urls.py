
from django.conf.urls import url

from api.views_dir import login, company, role, user, project, action, demand, img_upload, \
    permissions, project_env_switch, code_online, updatePwd


urlpatterns = [
    url(r'^login$', login.login),

    # 修改密码
    url(r'^updatePassword/(?P<oper_type>\w+)/(?P<o_id>\d+)', updatePwd.updatePassword),

    # 公司管理
    url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    url(r'^company', company.company),

    # 权限管理
    url(r'^permissions/(?P<oper_type>\w+)/(?P<o_id>\d+)', permissions.permissions_oper),
    url(r'^permissions', permissions.permissions),

    # 角色管理
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role$', role.role),

    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user$', user.user),

    # 项目/产品管理
    url(r'^project/(?P<oper_type>\w+)/(?P<o_id>\d+)', project.project_oper),
    url(r'^project$', project.project),

    # 功能管理
    url(r'^action/(?P<oper_type>\w+)/(?P<o_id>\d+)', action.action_oper),
    url(r'^action$', action.action),

    # 需求管理
    url(r'^demand/(?P<oper_type>\w+)/(?P<o_id>\d+)', demand.demand_oper),
    url(r'^demand$', demand.demand),


    url(r'^img_upload$', img_upload.img_upload),
    url(r'^img_merge$', img_upload.img_merge),
    url(r'^ueditor_img_upload$', img_upload.ueditor_image_upload),

    # 项目环境切换管理
    url(r'^project_env_switch/(?P<oper_type>\w+)/(?P<o_id>\d+)', project_env_switch.project_env_switch_oper),
    url(r'^project_env_switch$', project_env_switch.project_env_switch),

    # 项目代码上线
    url(r'^code_online/(?P<oper_type>\w+)/(?P<o_id>\d+)', code_online.code_online_oper),
    url(r'^code_online', code_online.code_online),


]
