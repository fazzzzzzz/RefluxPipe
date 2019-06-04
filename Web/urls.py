from django.urls import path, re_path

from Web import views

urlpatterns = [
    path('admin/', views.index, name='index'),
    path('admin/login', views.login, name='login'),
    path('admin/registe', views.registe, name='registe'),
    path('admin/account_info', views.account_info, name='accountInfo'),
    path('admin/account_setting', views.account_setting, name='accountSetting'),
    path('admin/admin_setting', views.admin_setting, name='adminSetting'),
    path('admin/dnslog', views.dnslog, name='dnslog'),
    path('admin/api/update_api_token', views.update_api_token, name='updateApiToken'),
    path('admin/api/table/dnslog', views.getTableDnslog, name='getTableDnslog'),
    path('admin/api/table/dnslog/del', views.delDnslog, name='delDnslog'),
    path('admin/api/table/user', views.getTableUser, name='getTableUser'),
    path('admin/api/table/user/del', views.delUser, name='delDnslog'),
    path('admin/api/table/invite_code', views.getTableInviteCode, name='getTableInviteCode'),
    path('admin/api/table/invite_code/del', views.delInviteCode, name='delInviteCode'),
    path('admin/api/table/invite_code/create', views.createInviteCode, name='createInviteCode'),
    path('admin/httplog', views.httplog, name='httplog'),
    path('admin/api/table/httplog', views.getTableHttplog, name='getTableHttplog'),
    path('admin/api/table/httplog/del', views.delHttplog, name='delHttplog'),
    path('admin/httplog', views.httplog, name='httplog'),
    path('admin/logout', views.logout, name='logout'),
    path('admin/api', views.queryapi, name='queryapi'),
    re_path(r'^.*$', views.recordhttplog, name='recordhttplog')
]
