from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserProfile(AbstractUser):
    """
    用户信息
    """
    GENDER_CHOICES = (
        ('male','男'),
        ('female','女')
    )

    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES, default="female", verbose_name="性别")
    mobile = models.CharField(null=True,blank=True,max_length=11,verbose_name="电话")
    email = models.EmailField(max_length=100,null=True,blank=True,verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username




class Verifycode(models.Model):
    """
    短信验证码,回填验证码进行验证
    """
    code = models.CharField(max_length=20,verbose_name="验证码")
    mobile = models.CharField(max_length=11,verbose_name="电话")
    add_time = models.DateTimeField(default=datetime.now,verbose_name="添加时间")

    class Meta:
        verbose_name = "短信验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code



