import json
from io import BytesIO
# import sys
# import time
from datetime import datetime
# import os
# import re  # 正则表达式

from django.shortcuts import render, HttpResponse, redirect
# from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.clickjacking import xframe_options_exempt
# from django.conf import settings
# from django.contrib import messages

from app01 import models
from app01.utils.create_code import check_code
from app01.utils.send_email import send_sms_code
from app01.utils.pagination import Pagination
from app01.utils.form import UserModelForm_signIn, UserModelForm_login, UserModelForm_edit_account, \
    UserModelForm_changePwd, UserModelForm_Log
# from app01.utils.form import LoginForm,CreateBugForm
from app01.utils.form import LoginForm,ForumForm,ForumCommentForm

# '''测试函数'''
# def test(request):
#     # send_sms_code()
#     return render(request,'test.html')


'''联系我们'''
def contact_us(request):
    return render(request, 'contact_us.html')


'''主页'''
def home(request):
    return redirect('/forum/0/category/')


'''注册'''
def signIn(request):
    if request.method == "GET":
        form = UserModelForm_signIn()
        return render(request, 'signIn.html', {"form": form})

    # 用户POST提交数据，进行数据校验
    form = UserModelForm_signIn(data=request.POST)
    get_verify = request.POST.get("verify")  # 获取用户输入的验证码
    verification_code = request.session.get('text_code', "")  # 获取存在session中的验证码
    if form.is_valid():  # 如果数据合法，保存到数据库
        if get_verify == verification_code:  # 如果验证码正确
            form.save()
            return redirect('/login/')
        else:
            return render(request, "signIn.html", {"form": form, "msg_warn": "邮箱验证码错误！"})

    # 校验失败，显示错误信息
    return render(request, 'signIn.html', {"form": form})


'''注册-验证数据合法性并调用发送邮件的函数'''
@csrf_exempt
def signin_check(request):
    form = UserModelForm_signIn(data=request.POST)
    # print(form)

    if form.is_valid():
        # 判断邮箱是否已经被注册过，数据库中是否已经存在数据
        choise = models.UserInfo.objects.filter(email=request.POST.get("email")).exists()

        # 如果choise==true，说明数据库已经存在这个邮箱
        if choise:
            # 获取这条数据的内容，判断是否已经被注销
            datalist = models.UserInfo.objects.filter(email=request.POST.get("email")).last()  # 获取最新数据
            if datalist.if_write_off == 1:  # 存在数据，但是那个账号已经被注销，也可以注册
                datas = form.save(commit=False)  # 获取用户已经输入的数据，但是不存入数据库，用作发送邮件
                to_email = datas.email
            else:
                dict = {"msg_warn": "邮箱已经被注册过！"}
                return HttpResponse(json.dumps(dict))
        else:  # 不存在信息，可以注册，发送验证邮件
            datas = form.save(commit=False)  # 获取用户已经输入的数据，但是不存入数据库，用作发送邮件
            to_email = datas.email
    else:
        data_dict = {'error': form.errors}
        return HttpResponse(json.dumps(data_dict, ensure_ascii=False))

    print(to_email)
    verification_code = send_sms_code(to_email)

    # 写入到自己的session中，方便后续获取验证码进行校验
    request.session['text_code'] = verification_code
    # 给session设置二十分钟超时,超出二十分钟后获取不到
    session_time = 60 * 20
    request.session.set_expiry(session_time)
    print(verification_code)

    dicti = {"msg_success": "邮箱验证码发送成功！"}
    return HttpResponse(json.dumps(dicti))


'''登录'''
def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 获取用户输入的验证码，并从cleaned_data中去除掉以防止影响数据库的判断
        user_input_code = form.cleaned_data.pop('code')
        code = request.session.get(
            'image_code')  # 在这里，如果在图片验证码那个函数里设置了session的过期时间，则要写为code = request.session.get('image_code', "")
        if code.upper() != user_input_code.upper():
            form.add_error("code", "验证码错误！")
            return render(request, 'login.html', {'form': form})

        # 去数据库校验数据是否正确
        admin_object = models.UserInfo.objects.filter(**form.cleaned_data).last()  # 校验是否存在这条数据，而且能获取到的包含已经注销的用户
        datalist = models.UserInfo.objects.filter(
            email=form.cleaned_data['email']).last()  # 获取邮箱为email的最新数据的所有内容，用于下一步判断是否已经注销
        if (not admin_object) or (datalist.if_write_off == 1):
            # 邮箱或者密码不正确(不存在数据) or 账户已经注销
            form.add_error("password", "邮箱或密码错误！")
            return render(request, 'login.html', {'form': form})

        # 邮箱和密码正确，获取当前登录的用户的ID，存储到session中
        # 用户名和密码都正确，生成随机字符串，写入到用户浏览器的cookie中，再写入到session中（此处session为一个字典）
        request.session["info"] = {"id": admin_object.id, 'email': admin_object.email, 'name': admin_object.name}
        keep_time = 5 * 24 * 60 * 60
        request.session.set_expiry(keep_time)  # 设置session过期时间为5天

        # datalist.update(last_login=datetime.datetime())
        models.UserInfo.objects.filter(email=form.cleaned_data['email']).update(last_login=datetime.now())
        return redirect('/home/')

    return render(request, 'login.html', {'form': form})


'''生成图片验证码'''
@csrf_exempt
def image_code(request):
    # 调用生成图片验证码的函数
    img, code_str = check_code()
    print("验证码为" + code_str)

    # 写入到自己的session中，方便后续获取验证码进行校验
    request.session['image_code'] = code_str
    # 给session设置120s超时,超出120s后获取不到
    # request.session.set_expiry(120)

    # 把生成的图片写入内存中
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


'''点击图片刷新验证码-Ajax'''
@csrf_exempt
def image_refresh(request):
    # 调用生成图片验证码的函数
    img, code_str = check_code()
    print("验证码为" + code_str)

    # 写入到自己的session中，方便后续获取验证码进行校验
    request.session['image_code'] = code_str
    # 给session设置120s超时,超出120s后获取不到
    request.session.set_expiry(120)

    # 把生成的图片写入内存中
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue(), content_type='image/png')


'''账户管理'''
def account(request):
    info = request.session.get("info")
    nid = info['id']
    email = info['email']
    queryset = models.UserInfo.objects.filter(email=email).last()  # 从数据库获取当前用户的对象
    # nid = queryset.id
    return render(request, 'account.html', {"queryset": queryset})


'''编辑信息'''
def edit_account(request, id):
    info = request.session.get("info")
    nid = info['id']
    email = info['email']

    row_object = models.UserInfo.objects.filter(id=nid).first()  # 如果能获取到，返回一个对象；获取不到返回None
    # 如果是none，则返回错误页面
    if not row_object:
        return render(request, '404.html')

    # print(email)
    # row_object = models.UserInfo.objects.filter(email=email).last()        #从数据库获取email为n_email的对象
    if request.method == "GET":
        form = UserModelForm_edit_account(instance=row_object)
        return render(request, 'account_edit.html', {"form": form})

    # 用户POST提交数据，进行数据校验
    form = UserModelForm_edit_account(data=request.POST, instance=row_object)
    if form.is_valid():
        # 如果数据合法，保存到数据库
        form.save()
        # 这里还可以优化：从用户提交的请求中获取数据，但是我现在没法查资料，不知道怎么写，先放这
        print(form.cleaned_data["name"])

        # 更新session
        email = form.cleaned_data["email"]
        id = models.UserInfo.objects.filter(email=email).last().id  # 由于用户提交的数据里没有ID，所以得先从数据库中获取用户的id
        request.session["info"] = {'id': id, 'email': email, 'name': form.cleaned_data["name"]}
        return redirect('/account/')

    # 校验失败，显示错误信息
    return render(request, 'account_edit.html', {"form": form})


'''退出登录'''
def quit_account(request):
    request.session.clear()
    return redirect('/home/')


'''注销'''
def write_off(request):
    info = request.session.get("info")
    nid = info['id']
    print(nid)
    models.UserInfo.objects.filter(id=nid).update(if_write_off=1)
    # models.UserInfo.objects.filter(id=nid).delete()
    request.session.clear()
    return redirect('/login/')


'''忘记密码'''
def forgot_pwd(request):
    if request.method == "GET":
        form = UserModelForm_changePwd()
        return render(request, 'forgot_pwd.html', {"form": form})

    form = UserModelForm_changePwd(data=request.POST)
    get_verify = request.POST.get("verify")  # 获取用户输入的验证码
    verification_code = request.session.get('retrieve_code', "")  # 获取存在session中的验证码

    if get_verify == verification_code:  # 如果验证码正确
        # request.session['pwd_change_email'] = request.POST.get("email")    #将要修改的邮箱写入session，便于后面调用
        if form.is_valid():
            models.UserInfo.objects.filter(email=form.cleaned_data["email"]).update(
                password=form.cleaned_data["password"])  # 修改数据库中的密码
            return redirect('/login/')  # 跳转到登录
        return render(request, 'forgot_pwd.html', {"form": form})
    else:
        return render(request, "forgot_pwd.html", {"form": form, "msg_warn": "邮箱验证码错误！"})


'''忘记密码-验证邮箱和发送邮件'''
@csrf_exempt
def forgot_pwd_code(request):
    # POST提交数据进行处理
    form = UserModelForm_changePwd(data=request.POST)
    # if form.is_valid():

    # 判断邮箱是否已经被注册过，数据库中是否已经存在数据
    choise = models.UserInfo.objects.filter(email=request.POST.get("email")).exists()
    if choise:
        datalist = models.UserInfo.objects.filter(email=request.POST.get("email")).last()  # 获取最新数据
        if datalist.if_write_off == 1:  # 存在数据，但是那个账号已经被注销，不能找回
            dict = {"msg_warn": "邮箱不存在！"}
            return HttpResponse(json.dumps(dict))
        else:
            to_email = datalist.email
            print(to_email)

    else:  # 数据库不存在该邮箱
        dict = {"msg_warn": "邮箱不存在！"}
        return HttpResponse(json.dumps(dict))

    # 邮箱校验成功，发送邮件
    verification_code = send_sms_code(to_email)
    # 写入到自己的session中，方便后续获取验证码进行校验
    request.session['retrieve_code'] = verification_code
    # 给session设置二十分钟超时,超出二十分钟后获取不到
    session_time = 60 * 20
    request.session.set_expiry(session_time)
    print(verification_code)

    dict = {"msg_success": "邮箱验证码发送成功！"}
    return HttpResponse(json.dumps(dict))



'''只有管理员可访问的url'''
'''管理员-面板'''
def admin_main(request):
    return render(request, 'admin_main.html')


'''管理员-登入'''
def admin_login(request):
    if request.method == "GET":
        title = "管理员-登入"
        return render(request, 'history_login.html', {"title": title})

    # 用户以POST方式提交秘钥，进行判断
    get_pwd = request.POST.get("password")
    if get_pwd == "A1d2m3i4n5":
        request.session['admin'] = "admin"
        keep_time = 14 * 24 * 60 * 60
        request.session.set_expiry(keep_time)  # 设置session过期时间为两周
        return redirect('/admin/main/')
    else:
        return render(request, 'history_login.html', {"msg_warn": "秘钥错误，你得注意一下~", "get_pwd": get_pwd})


'''管理员-用户列表'''
def admin_user_list(request):
    title = "用户管理"
    queryset = models.UserInfo.objects.all()

    # 实例化分页对象
    page_object = Pagination(request, queryset)

    context = {
        "queryset": queryset,
        "title": title,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 生成页码
    }
    return render(request, 'admin_user_list.html', context)


'''管理员-删除用户'''
def admin_user_delete(request, id):
    models.UserInfo.objects.filter(id=id).delete()
    return redirect('/admin/user_list/')


'''管理员-编辑用户'''
def admin_user_edit(request, id):
    # form = models.UserInfo.objects.filter(id=id)
    row_object = models.UserInfo.objects.filter(id=id).last()  # 如果能获取到，返回一个对象；获取不到返回None

    # 如果是none，则返回错误页面
    if not row_object:
        return render(request, '404.html')

    if request.method == "GET":
        form = UserModelForm_edit_account(instance=row_object)
        title = "编辑用户"
        return render(request, 'admin_edit.html', {"form": form, "title": title})

    # 用户POST提交数据，进行数据校验
    form = UserModelForm_edit_account(data=request.POST, instance=row_object)
    if form.is_valid():
        # 如果数据合法，保存到数据库
        form.save()
        return redirect('/admin/user_list/')

    # 校验失败，显示错误信息
    return render(request, 'admin_edit.html', {"form": form})


'''管理员-查看日志'''
def admin_log(request):
    queryset = models.Log.objects.all().order_by("-id")
    # queryset = models.Log.objects.all().order_by("-version_num")
    # queryset = models.Log.objects.all().order_by("-time")
    page_object = Pagination(request, queryset)

    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 生成页码
    }
    return render(request, 'admin_log.html', context)


'''管理员-新建日志'''
def admin_creat_log(request):
    if request.method == "GET":
        form = UserModelForm_Log()
        for i in form:
            print(i)
        return render(request, 'admin_log_creat.html', {"form": form})

    form = UserModelForm_Log(data=request.POST)
    if form.is_valid:
        print("合法")
        form.save()
        return redirect('/admin/log/')
    # 校验失败，显示错误信息
    print("校验失败")
    return render(request, 'admin_log_creat.html', {"form": form})


'''管理员-编辑日志'''
def admin_log_edit(request, id):
    row_object = models.Log.objects.filter(id=id).last()  # 如果能获取到，返回一个对象；获取不到返回None

    # 如果是none，则返回错误页面
    if not row_object:
        return render(request, '404.html')

    if request.method == "GET":
        form = UserModelForm_Log(instance=row_object)
        title = "编辑日志"
        return render(request, 'admin_edit.html', {"form": form, "title": title})

    # 用户POST提交数据，进行数据校验
    form = UserModelForm_Log(data=request.POST, instance=row_object)
    if form.is_valid():
        # 如果数据合法，保存到数据库
        form.save()
        return redirect('/admin/log/')

    # 校验失败，显示错误信息
    return render(request, 'admin_edit.html', {"form": form})


'''管理员-删除日志'''
def admin_log_delete(request, id):
    models.Log.objects.filter(id=id).delete()
    return redirect('/admin/log/')


'''管理员-论坛管理'''
def admin_forum(request,content_type):  #content_type:  1-待审核帖子；2-已发布帖子；3-待审核评论；4-已发布评论
    corresponding = {
        1:1,    #已发布帖子在forum表中对应的status为1，下同
        2:2,
        3:1,    #已发布评论在comment表中对应的status为1，下同
        4:2,
    }
    if content_type == 1 or content_type == 2:  #如果查看的是帖子
        queryset = models.Forum.objects.filter(status=corresponding[content_type]).order_by('-id')
    elif content_type == 3 or content_type == 4:  #如果查看的是评论
        queryset = models.ForumComments.objects.filter(status=corresponding[content_type]).order_by('-id')
    else:
        return redirect('/admin/1/forum/')

    request.session['admin_forum_original_path'] = request.path
    return render(request,'admin_forum.html',{"queryset":queryset})


'''管理员-审核帖子'''
def admin_forum_psg(request,psg_id,access):
    original_path = request.session.get('admin_forum_original_path')
    # print(type(original_path[7]))
    if original_path[7] == "1" or original_path[7] == "2":      #审核帖子
        if access == 0:     #审核未通过
            models.Forum.objects.filter(id=psg_id).update(status=3)
        elif access == 1:   #审核通过
            models.Forum.objects.filter(id=psg_id).update(status=2)
        else:
            pass

    elif original_path[7] == "3" or original_path[7] == "4":    #审核评论
        if access == 0:     #审核未通过
            models.ForumComments.objects.filter(id=psg_id).update(status=3)
        elif access == 1:   #审核通过
            models.ForumComments.objects.filter(id=psg_id).update(status=2)
        else:
            pass
    else:
        pass

    return redirect(original_path)



'''纪念馆'''
def museum(request):
    return render(request, 'museum.html')


'''更新日志'''
def museum_log(request):
    # for i in range(1,300):
    #    models.Log.objects.create(version_num="1",time="2023.4.5",substance="刀灵")
    queryset = models.Log.objects.all().order_by("-id")

    page_object = Pagination(request, queryset)

    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 生成页码
    }
    print(context)

    return render(request, 'museum_log.html', context)


'''关于我们'''
def museum_about_us(request):
    return render(request, 'museum_about_us.html')


'''论坛首页'''
def forum_main(request,category):
    info = request.session.get("info")
    if not info:
        user_name = "未登录"
        id = 0
    else:
        user_name = info['name']
        id = info['id']

    data_dict = {"category":category,"status":2}      #查询条件：对应领域、审核通过
    value = request.GET.get("q")    #从前端获取到查询内容

    if value:   #如果非空
        data_dict["title__contains"] = value
    dic = {
        0: "",
        1: "-公告",
        2: "-推荐",
        3: "-最新",
        4: "-热门",
    }
    try:
        classification = dic[category]
    except KeyError:    #如果访问的category在[0,4]之外，重定向到首页
        return redirect('/forum/0/category/')

    if category == 0:   #如果访问的是首页
        if value:   #如果非空
            queryset1 = models.Forum.objects.filter(status=2,title__contains=value)
            queryset2 = models.Forum.objects.filter(status=2,content__contains=value)
            queryset = queryset1.union(queryset2).order_by('-id')
        else:   #如果是空的，即查看的是所有内容
            queryset = models.Forum.objects.filter(status=2,title__contains="").order_by('-id')
    else:
        queryset = models.Forum.objects.filter(**data_dict).order_by('-id')

    for q in queryset:
        if len(q.content) >= 40:
            content = q.content[0:40] + "..."       #只获取内容的前40个字符
        else:
            content = q.content
        setattr(q, "content", content)      #把内容的前40个字符添加为object对象的属性

        username = models.UserInfo.objects.filter(id=q.user).first().name   #通过id获取发布帖子的用户名
        setattr(q,"username",username)      #给每个获取到的Forum object对象添加username属性，属性值为上一行获取到的username，从而方便前端获取用户名

    page_object = Pagination(request, queryset)

    context = {
        "user_name": user_name,
        "user_id": id,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
        "category": classification,
    }
    return render(request, 'forum_main.html',context)


'''论坛-发布帖子'''
def forum_post(request):
    info = request.session.get("info")
    #name = info['name']

    if request.method == "GET":
        form = ForumForm()
        context = {
            "form": form,
            "user_name":info['name'],
            "user_id": info['id'],
        }
        return render(request, 'forum_post.html', context)

    form = ForumForm(data=request.POST)
    if form.is_valid():
        #print(form.cleaned_data)
        #content = form.cleaned_data['content'].replace("/n", "<br>")
        models.Forum.objects.create(
            title=form.cleaned_data['title'],
            content=form.cleaned_data['content'],
            publishDate=None,
            user=info["id"],
        )
        return redirect('/forum/0/category/')
    context = {
        "form": form,
        "user_name": info['name'],
        "user_id":info['id'],
    }
    return render(request,'forum_post.html',context)



'''论坛-查看帖子和评论'''
def forum_passage(request,psg_id):
    info = request.session.get("info")
    user_name = info['name']
    id = info['id']

    passage_obj = models.Forum.objects.filter(id=psg_id).first()    #获取文章对象
    admin_judge = request.session['admin']
    print(admin_judge)
    if not admin_judge:     #不是管理员查看
        if (passage_obj.status != 2) and (passage_obj.user != id):  # 如果没有过审，且该文章的作者不是自己，重定向回首页
            return redirect('/forum/0/category/')

    author = models.UserInfo.objects.filter(id=passage_obj.user).first().name  # 通过id获取发布帖子的用户名
    setattr(passage_obj, "author", author)  # 给每个获取到的Forum object对象添加username属性，属性值为上一行获取到的username，从而方便前端获取用户名

    comments_obj = models.ForumComments.objects.filter(passage_id=psg_id).order_by('-id')   #筛选出这篇文章的评论
    for cmt_obj in comments_obj:
        print(cmt_obj.content)
        cmt_user = models.UserInfo.objects.filter(id=cmt_obj.user).first()  #获取发布该评论的用户
        setattr(cmt_obj,"cmt_user",cmt_user.name)

    if request.method == "GET":
        form = ForumCommentForm()
        context = {
            "passage_obj": passage_obj,
            "user_name": user_name,
            "user_id": id,
            "form":form,
            "comments_obj":comments_obj,
        }
        return render(request, 'forum_passage.html', context)

    #用POST返回评论
    form = ForumCommentForm(data=request.POST)
    if form.is_valid():
        models.ForumComments.objects.create(
            user=id,
            content=form.cleaned_data['content'],
            publishDate=None,
            passage_id=psg_id
        )
        return redirect('/forum/'+str(psg_id)+'/passage/')
    context = {
        "passage_obj": passage_obj,
        "user_name": user_name,
        "user_id": id,
        "form": form,
    }
    return render(request,'forum_passage.html',context)


'''论坛-个人主页'''
def forum_author(request,user_id):
    info = request.session.get("info")
    user = models.UserInfo.objects.filter(id=user_id).first()

    if user:    #如果用户存在
        if user_id == info['id']:  # 如果访问的是自己的主页
            queryset = models.Forum.objects.filter(user=user_id, status__in=[1,2,3]).order_by('-id')  # 筛选除了状态4以外的数据，即没有被删除的(访问自己的主页时可以看到待审核和审核未通过的)
        else:
            queryset = models.Forum.objects.filter(user=user_id, status=2).order_by('-id')  #访问的是别人的主页，因此筛选出审核已通过的

        for q in queryset:
            if len(q.content) >= 40:
                content = q.content[0:40] + "..."  # 只获取内容的前40个字符
            else:
                content = q.content
            setattr(q, "content", content)

        page_object = Pagination(request, queryset)

        context = {
            "user_name": info['name'],  # 右上角显示的当前登录的用户名
            "user_id": info['id'],
            "name": user.name,  # 当前查看的用户名
            "queryset": page_object.page_queryset,  # 分完页的数据
            "page_string": page_object.html(),  # 生成页码
        }

        if user_id == info['id']:  # 如果访问的是自己的主页
            return render(request, 'forum_myself.html',context)

        #不是自己的主页
        return render(request,'forum_author.html',context)
    return redirect('/forum/0/category/')


'''论坛-删除帖子'''
def forum_delete(request,psg_id):
    info = request.session.get("info")
    models.Forum.objects.filter(id=psg_id,user=info['id']).update(status=4)     #属性设置为删除
    return redirect('/forum/'+str(info['id'])+'/author/')



