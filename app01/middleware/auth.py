from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse,redirect,render

class AuthIfLogin(MiddlewareMixin):
    """ 验证用户是否已经登录 """
    def process_request(self, request):
        # 排除那些不需要登录就能访问的页面
        exclusions = [
            '/test/',
            '/login/',
            '/signIn/',
            '/send_sms_code/',
            '/image/code/',
            '/image/refresh/',
            '/home/',
            '/forgot/pwd/',
            '/forgot/pwd/code/',
            '/forgot/pwd/change/',
            '/admin/main/',
            '/admin/login/',
            '/admin/user_list/',
            '/admin/<int:id>/user_delete/',
            '/admin/<int:id>/user_edit/',
            '/admin/log/',
            '/admin/creat_log/',
            '/admin/<int:id>/log_edit/',
            '/admin/<int:id>/log_delete/',
            '/admin/forum/',
            '/admin/forum/passage/released/',

            '/forum/0/category/',
            '/forum/1/category/',
            '/forum/2/category/',
            '/forum/3/category/',
            '/forum/4/category/',
            #'/md/<int:user_id>/<int:file_id>/edit/',
        ]

        # 获取当前访问用户的session信息
        info_dict = request.session.get("info")
        if info_dict:
            #能读到信息说明已经登录过
            lists = [
                # '/home/',
                '/admin/main/',
                '/admin/login/',
                '/admin/user_list/',
                '/admin/<int:id>/user_delete/',
                '/admin/<int:id>/user_edit/',
                '/admin/log/',
                '/admin/creat_log/',
                '/admin/<int:id>/log_edit/',
                '/admin/<int:id>/log_delete/',
                '/admin/forum/',
                '/admin/forum/passage/released/',

                '/forum/0/category/',
                '/forum/1/category/',
                '/forum/2/category/',
                '/forum/3/category/',
                '/forum/4/category/',
            ]
            for i in lists:
                exclusions.remove(i)    #移除即使登录，也能访问的页面

            if request.path_info in exclusions:     #如果已经登录，但是仍然访问了这些页面，重定向到主页
                return redirect('/forum/0/category/')
            return  #访问的页面不在exclusions中，返回None，继续访问

        else:  #如果没有登录
            if request.path_info in exclusions:
                #如果没有登录，但是访问的链接在exclusions中，可以访问
                return
            return redirect('/login/')  #读不到session，跳转登录


    def process_response(self, request, response):
        #print("M1.process_response")
        return response



class AuthIfAdmin(MiddlewareMixin):
    """ 验证用户是否为管理员 """
    def process_request(self, request):
        # 那些管理员才能访问的页面
        exclusions = [
            '/admin/main/',
            #'/admin/login/',
            '/admin/user_list/',
            '/admin/<int:id>/user_delete/',
            '/admin/<int:id>/user_edit/',
            '/admin/log/',
            '/admin/creat_log/',
            '/admin/<int:id>/log_edit/',
            '/admin/<int:id>/log_delete/',
            '/admin/forum/',
            '/admin/forum/passage/released/',
        ]

        #如果访问了上面这些链接
        if request.path_info in exclusions:
            #判断是否有管理员的session
            info_dict = request.session.get("admin")
            if info_dict:   #如果能获取到，说明是管理员，继续访问
                return
            return redirect('/admin/login/')
        return  #访问的页面不在exclusions中，返回None，继续访问

    def process_response(self, request, response):
        #print("M1.process_response")
        return response

