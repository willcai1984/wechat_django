from django.db import models
import django.utils.timezone as timezone


# Create your models here.
class User(models.Model):
    open_id = models.CharField('用户在微信的openid，全局唯一', max_length=32, default='')
    nick_name = models.CharField('用户在微信的昵称，可修改', max_length=50, default='')
    create_time = models.DateTimeField('创建日期', default=timezone.now)
    img_url = models.CharField('用户在微信头像', max_length=64, default='')
    is_delete = models.IntegerField('逻辑删除，默认0，0正常，1删除', default=0)


class Accout(models.Model):
    account_id = models.CharField('账号id，全局唯一', max_length=16, default='')
    open_id = models.CharField('用户在微信的openid，全局唯一', max_length=32, default='')
    src_web = models.CharField('账号网站，如人人网', max_length=32, default='人人网')
    user_name = models.CharField('账号网站的用户名，同一open_id向下，src_web+user_name唯一', max_length=32, default='')
    user_password = models.CharField('账号网站的密码', max_length=32, default='')
    user_status = models.IntegerField('账号状态，默认为0，0待抓取，1抓取中，2抓取成功，3抓取失败', default=0)
    create_time = models.DateTimeField('创建日期', default=timezone.now)
    update_time = models.DateTimeField('最近一次修改日期', default=timezone.now)
    is_delete = models.IntegerField('逻辑删除，默认0，0正常，1删除', default=0)


class Account_detial(models.Model):
    account_id = models.CharField('账号id，全局唯一', max_length=16, default='')
    blog_url = models.CharField('账号id的blog文件的存储url', max_length=32, default='')
    blog_password = models.CharField('账号id的blog文件解压密码', max_length=32, default='')
    photo_url = models.CharField('账号id的photo文件的存储url', max_length=32, default='')
    photo_password = models.CharField('账号id的photo文件解压密码', max_length=32, default='')
    is_pay = models.IntegerField('支付判断位，默认0，0未付款，1已付款', default=0)
    pay_serial_no = models.CharField('微信支付流水号', max_length=40)
    is_delete = models.IntegerField('逻辑删除，默认0，0正常，1删除', default=0)
