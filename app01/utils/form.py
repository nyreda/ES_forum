# 所有的form都在这里，创建新的form后记得在views.py中调用！！
from app01 import models
from django import forms

from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.bootstrap import BootStrapForm
from django.core.exceptions import ValidationError

import string

'''注册'''
class UserModelForm_signIn(BootStrapModelForm):
    #限制条件，密码必须在6位以上，邮箱必须格式正确
    #password = forms.CharField(min_length=6,label="密码")
    email = forms.EmailField(label="邮箱")
    password = forms.CharField(label='密码', min_length=6, widget=forms.PasswordInput(render_value=True))
    confirm_password = forms.CharField(label="确认密码",widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.UserInfo
        fields = ["name","email","password","confirm_password"]

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm_pwd = self.cleaned_data.get("confirm_password")
        if pwd != confirm_pwd:
            raise ValidationError("密码不一致")
        return confirm_pwd      #return什么，此字段以后保存到数据库的数据就是什么


'''登录'''
class UserModelForm_login(BootStrapModelForm):
    #password = forms.PasswordInput(label="密码")
    email = forms.EmailField(label="邮箱")
    code = forms.CharField(label="验证码")
    class Meta:
        model = models.UserInfo
        fields = ["email","password","code"]

        widgets = {
            "password":forms.PasswordInput(render_value=True),
        }


'''编辑账号'''
class UserModelForm_edit_account(BootStrapModelForm):
    password = forms.CharField(min_length=6,label="密码")
    email = forms.CharField(disabled=True,label = "邮箱")

    class Meta:
        model = models.UserInfo
        fields = ["email","name","password"]

        widgets = {
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.TextInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"}),
        }



'''登录'''
class LoginForm(forms.Form):
    email = forms.CharField(
        label="邮箱",
        widget=forms.TextInput(attrs={"class":"form-control"}),
        required=True
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"class":"form-control"},render_value=True),
        required=True
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(attrs={"class":"form-control"}),
        required=True
    )



'''重置密码'''
class UserModelForm_changePwd(BootStrapModelForm):
    #限制条件，密码必须在6位以上，邮箱必须格式正确
    #password = forms.CharField(min_length=6,label="密码")
    email = forms.EmailField(label="邮箱")
    password = forms.CharField(label='密码', min_length=6, widget=forms.PasswordInput(render_value=True))
    confirm_password = forms.CharField(label="确认密码",widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.UserInfo
        fields = ["email","password","confirm_password"]

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm_pwd = self.cleaned_data.get("confirm_password")
        if pwd != confirm_pwd:
            raise ValidationError("密码不一致")
        return confirm_pwd      #return什么，此字段以后保存到数据库的数据就是什么




'''管理员-编辑用户'''
class UserModelForm_edit_account(BootStrapModelForm):
    password = forms.CharField(min_length=6,label="密码")
    email = forms.CharField(disabled=True,label = "邮箱")

    class Meta:
        model = models.UserInfo
        fields = ["email","name","password"]

        widgets = {
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.TextInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"}),
        }


'''管理员-编辑日志'''
class UserModelForm_Log(BootStrapModelForm):
    class Meta:
        model = models.Log
        fields = ["version_num","substance","developer"]

        widgets = {
            "version_num":forms.TextInput(attrs={"class":"form-control"}),
            "substance":forms.Textarea(attrs={"class":"form-control"}),
        }


class ForumForm(forms.Form):
    '''论坛帖子'''
    title = forms.CharField(
        label="标题",
        widget=forms.TextInput(attrs={"class":"form-control"}),
        required=True
    )
    content = forms.CharField(
        label="内容",
        widget=forms.Textarea(attrs={"class":"form-control"}),
        required=True
    )


class ForumCommentForm(forms.Form):
    '''论坛评论'''
    content = forms.CharField(
        label="内容",
        widget=forms.Textarea(attrs={"class":"form-control"}),
        required=True
    )






'''

from app01.models import Markdown
from mdeditor.fields import MDTextFormField

class CreateBugForm(forms.Form):
    md = MDTextFormField(label="", widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=65535)

class MDEditorModelForm(forms.ModelForm):
    class Meta:
        model = models.Markdown
        fields = '__all__'
        
'''


'''
import markdown2

class MarkdownEditorForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
    preview = forms.CharField(required=False, widget=forms.Textarea, disabled=True)

    def clean_content(self):
        content = self.cleaned_data.get('content')
        preview = markdown2.markdown(content)
        self.cleaned_data['preview'] = preview
        return content
'''

# from django import forms
# #from models.markdown_editor import Markdown
'''
class MarkdownForm(forms.ModelForm):
    class Meta:
        model = models.Markdown
        fields = ('title', 'content')

'''

# class UpForm(forms.Form):
#     md = forms.FileField(label="markdown文件")
#
# class MdNameForm(forms.Form):
#     name = forms.CharField(
#         label="文件名",
#         widget=forms.TextInput(attrs={"class":"form-control"}),
#         required=True
#     )

#class MdReaNameForm(forms.Form):
