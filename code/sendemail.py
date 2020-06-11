# -*- coding: utf-8 -*-
"""
  @Author: zzn
  @Date: 2019-12-23 09:20:43
  @Last Modified by:   zzn
  @Last Modified time: 2019-12-23 09:20:43
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def send_register_email(to):
    sender_mail = 'support@uavecosystem.cn'
    msg_root = MIMEMultipart('mixed')
    msg_root['From'] = '飞客社区<support@uavecosystem.cn>'
    msg_root['To'] = to
    subject = '欢迎加入飞客社区'
    msg_root['subject'] = Header(subject, 'utf-8')
    text_info = '您好,\n\n欢迎您加入飞客社区!\n\nuavecosystem.cn'
    text_sub = MIMEText(text_info, 'plain', 'utf-8')
    msg_root.attach(text_sub)
    try:
        smtp_obj = smtplib.SMTP('uavecosystem.cn', 25)
        smtp_obj.login(sender_mail, '123456')
        smtp_obj.sendmail(sender_mail, to, msg_root.as_string())
        smtp_obj.quit()
        print('sendmail successful!')
    except Exception as e:
        print('sendmail failed:', e)


def send_postreply_email(from_username, to_username, to_useremail, post_title, reply_content_html):
    sender_mail = 'support@uavecosystem.cn'
    msg_root = MIMEMultipart('mixed')
    msg_root['From'] = '飞客社区<support@uavecosystem.cn>'
    msg_root['To'] = to_useremail
    subject = '飞客社区消息提醒'
    msg_root['subject'] = Header(subject, 'utf-8')
    start = '<p>{}</p>'.format(to_username)
    start += '<p>您好,</p><br>'
    start += '<p>用户"{}"在帖子《{}》中回复了您:</p>'.format(from_username, post_title)
    end = '<br><p>uavecosystem.cn</p>'
    reply_content_html = start+reply_content_html+end
    print(reply_content_html)
    content = MIMEText(reply_content_html, 'html', 'utf-8')
    msg_root.attach(content)
    try:
        smtp_obj = smtplib.SMTP('uavecosystem.cn', 25)
        smtp_obj.login(sender_mail, '123456')
        smtp_obj.sendmail(sender_mail, to_useremail, msg_root.as_string())
        smtp_obj.quit()
        print('sendmail successful!')
    except Exception as e:
        print('sendmail failed:', e)


if __name__ == '__main__':
    send_register_email('zzn@smail.nju.edu.cn')
