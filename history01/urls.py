"""history01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path,re_path
from app01 import views
# from django.views.static import serve
# from django.conf import settings

urlpatterns = [
    # re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),      #配置media
#    path('admin/', admin.site.urls),
#     path('test/', views.test),  # 测试页面
    #re_path(r'^$',views.home),

    #基本页面
    path('home/', views.home),      #主页
    path('', views.home),      #主页
    path('signIn/', views.signIn),  #注册
    path('login/', views.login),    #登录
    path('send_sms_code/', views.signin_check),    # 在注册界面发送验证邮件
    path('image/code/', views.image_code),  # 在登录界面生成图片验证码
    path('image/refresh/', views.image_refresh),  # 刷新验证码
    path('forgot/pwd/', views.forgot_pwd),  # 忘记密码
    path('forgot/pwd/code/', views.forgot_pwd_code),  # 忘记密码界面发送邮箱验证码
    path('contact_us/', views.contact_us),  # 联系我们


    #论坛
    path('forum/<int:category>/category/',views.forum_main),    #论坛主页
    path('forum/post/',views.forum_post),    #发布帖子
    path('forum/<int:psg_id>/passage/',views.forum_passage),    #论坛-查看帖子
    path('forum/<int:psg_id>/delete/',views.forum_delete),    #论坛-删除帖子
    path('forum/<int:user_id>/author/',views.forum_author),    #论坛-个人主页



    #纪念馆
    #path('museum/', views.museum),  # 纪念馆
    path('museum/log/', views.museum_log),  # 更新日志
    path('museum/about_us/', views.museum_about_us),  # 关于我们
    # path('museum/agreements/', views.museum_agreements),  # 协议



    #账户管理
    path('account/', views.account),    #账户管理
    path('edit/<int:id>/account/', views.edit_account),    #修改账户信息
    path('write_off/account/', views.write_off),    #注销账户
    path('quit/account/', views.quit_account),    #注销账户


    # #二班史册
    # path('history/content/', views.history_main),    #二班史册 主页
    # path('history/login/', views.history_login),    #二班史册 登录页
    # path('history/overview/content/', views.history_overview),    #二班史册 内容 概述
    # path('history/<int:chapter>/<int:section>/content/', views.history_frame),    #二班史册 内容 章节

    #管理员方可访问的页面
    path('admin/main/', views.admin_main),  # 管理员 面板
    path('admin/login/', views.admin_login),  # 管理员 面板
    path('admin/user_list/', views.admin_user_list),      #用户管理
    path('admin/<int:id>/user_delete/', views.admin_user_delete),      #编辑用户
    path('admin/<int:id>/user_edit/', views.admin_user_edit),      #删除用户
    path('admin/log/', views.admin_log),  # 日志管理
    path('admin/creat_log/', views.admin_creat_log),  # 日志管理
    path('admin/<int:id>/log_edit/', views.admin_log_edit),  # 编辑日志
    path('admin/<int:id>/log_delete/', views.admin_log_delete),  # 删除日志
    path('admin/<int:content_type>/forum/',views.admin_forum),     #论坛管理    1-待审核帖子；2-已发布帖子；3-待审核评论；4-已发布评论
    path('admin/forum/<int:psg_id>/<int:access>/psg/',views.admin_forum_psg),  #论坛管理-审核是/否通过     0-未通过；1-通过
    #path('admin/forum/passage/released/',views.admin_forum_passage_released),     #论坛管理=管理已发布帖子



    #path('signIn/', views.signIn),  #评论管理
    #path(r"^$",views.home),


    #path('editor/', views.md, name='editor'),

    # # 在线markdown
    # path('md/<int:user_id>/<int:file_id>/edit/',views.md_edit, name='markdown'),       #编辑文件
    # path('md/<int:id>/files/',views.md_files),       #管理文件
    # path('md/<int:user_id>/<int:obj_id>/delete/', views.md_delete),  # 删除
    # path('md/<int:user_id>/<int:obj_id>/rename/', views.md_rename),  # 重命名
    # path('md/<int:user_id>/<int:obj_id>/download/', views.md_download),  # 下载
    # path('md/upload/',views.md_upload),       #上传文件

    # re_path(r'^$',views.home),
]
