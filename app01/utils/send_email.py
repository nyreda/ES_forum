'''发送验证邮件'''
import random
from django.core.mail import send_mail



def send_sms_code(to_email):
    # 生成6位邮箱验证码
    verification_code = str(random.randint(100001, 999999))
    # print("验证码为"+verification_code)
    EMAIL_FROM = "hwHISTORY@foxmail.com"  # 邮箱来自
    email_title = '邮箱验证'  # 邮件主题
    email_body = "您的邮箱验证码为：" + verification_code + ", 该验证码有效时间为二十分钟，请及时进行验证。"  # 邮件内容
    #print("dl")

    # send_mail(email_title, email_body, EMAIL_FROM, [to_email])
    print(to_email)
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [to_email])

    return verification_code


