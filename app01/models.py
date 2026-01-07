from django.db import models

# Create your models here.
class UserInfo(models.Model):
    '''用户信息'''
    name = models.CharField(verbose_name="用户名",max_length=7)
    email = models.CharField(verbose_name="邮箱",max_length=128)
    password = models.CharField(verbose_name="密码",max_length=64)
    write_off_choices = (
        (1,'已注销'),
        (2,'未注销'),
    )
    if_write_off = models.SmallIntegerField(verbose_name="是否已经注销",choices = write_off_choices,default=2)    #已经注销，值为1，没有注销为2，默认为2
    last_login = models.DateTimeField(verbose_name="上次登录时间", auto_now=True)




class Log(models.Model):
    '''更新日志'''
    version_num = models.CharField(verbose_name="版本号",max_length=64)
    publishTime = models.DateTimeField(verbose_name="时间", auto_now=False,auto_now_add=True)
    substance = models.TextField(verbose_name="内容",max_length=1024)
    developer_choices = (
        (1, 'wezy'),
        (2, 'other（待完善）'),
    )
    developer = models.SmallIntegerField(verbose_name="开发者",choices=developer_choices,default=1)



class Forum(models.Model):
    '''论坛帖子'''
    title = models.CharField(verbose_name="标题",max_length=64)
    content = models.TextField(verbose_name="内容",max_length=2048)
    user = models.IntegerField(verbose_name="所属用户id")   #用于和userInfo表关联
    publishDate = models.DateTimeField(verbose_name="发布时间", auto_now=True)
    category_choices = (    #所属板块
        (1, '公告'),
        (2, '推荐'),
        (3, '最新'),
        (4, '热门'),
    )
    category = models.SmallIntegerField(verbose_name="所属板块",choices=category_choices,default=3)
    status_choices = {
        (1, '待审核'),
        (2, '审核通过'),
        (3, '审核未通过'),
        (4, '已删除'),
    }
    status = models.SmallIntegerField(verbose_name="状态",choices=status_choices,default=1)


class ForumComments(models.Model):
    '''论坛评论'''
    user = models.IntegerField(verbose_name="所属用户id")  # 用于和userInfo表关联
    content = models.TextField(verbose_name="内容",max_length=1024)
    publishDate = models.DateTimeField(verbose_name="发布时间", auto_now=True)
    passage_id = models.IntegerField(verbose_name="所属帖子id")   #用于和forum表关联
    status_choices = {
        (1, '待审核'),
        (2, '审核通过'),
        (3, '审核未通过'),
        (4, '已删除'),
    }
    status = models.SmallIntegerField(verbose_name="状态",choices=status_choices,default=1)


