
from django.conf.urls import url

from api.views_dir import login, company, role, user, project, action, demand, img_upload, \
    permissions, project_env_switch, code_online, updatePwd, caseInterfaceGrouping, caseInterfaceDetaile, \
    configurationManagementHOST, switch_nginx_huidu_ip, caseinter_project


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
    url(r'^pushMessageToWeChat$', demand.pushMessageToWeChat), # 定时刷新 判断需求创建时间 推送企业微信 及时完成开发


    url(r'^img_upload$', img_upload.img_upload),
    url(r'^img_merge$', img_upload.img_merge),
    url(r'^ueditor_img_upload$', img_upload.ueditor_image_upload),

    # 项目环境切换管理
    url(r'^project_env_switch/(?P<oper_type>\w+)/(?P<o_id>\d+)', project_env_switch.project_env_switch_oper),
    url(r'^project_env_switch$', project_env_switch.project_env_switch),

    # 项目代码上线
    url(r'^code_online/(?P<oper_type>\w+)/(?P<o_id>\d+)', code_online.code_online_oper),
    url(r'^code_online', code_online.code_online),

    # ------------------------------------------=测试用例=-----------------------------------------

    # 测试用例 项目管理
    url(r'^caseinter_project/(?P<oper_type>\w+)/(?P<o_id>\d+)$', caseinter_project.caseinter_project_oper),
    url(r'^caseinter_project', caseinter_project.caseinter_project),

    # 测试用例 接口分组
    url(r'^testCaseGroup/(?P<oper_type>\w+)/(?P<o_id>\d+)$', caseInterfaceGrouping.testCaseGroupOper),
    url(r'^testCaseGroup$', caseInterfaceGrouping.testCaseGroup),

    # 测试用例 接口详情
    url(r'^startTestCase', caseInterfaceDetaile.startTestCase),  # 启用测试用例
    url(r'^testCaseDetaile/(?P<oper_type>\w+)/(?P<o_id>\d+)$', caseInterfaceDetaile.testCaseDetaileOper),
    url(r'^testCaseDetaile$', caseInterfaceDetaile.testCaseDetaile),

    # 测试用例 host配置
    url(r'^configurationHost/(?P<oper_type>\w+)/(?P<o_id>\d+)$', configurationManagementHOST.configurationHostOper),
    url(r'^configurationHost$', configurationManagementHOST.configurationHost),

    # --------------------------------------------------------------------------------------------

    # 更换nginx中的灰度ip
    url(r'^switch_nginx_huidu_ip/(?P<oper_type>\w+)', switch_nginx_huidu_ip.switch_nginx_huidu_ip_oper),
    url(r'^switch_nginx_huidu_ip', switch_nginx_huidu_ip.switch_nginx_huidu_ip),

    # # 灰度环境ip切换
    # url(r'^huidu_ip_switch/(?P<oper_type>\w+)/(?P<o_id>\d+)', huidu_ip_switch.huidu_ip_switch_oper),
    # url(r'^huidu_ip_switch', huidu_ip_switch.huidu_ip_switch),
]
