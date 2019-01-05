# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\12\11 0011 21:37$'
"""
信号量
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

#参数一接受哪种信号，参数二是接受哪个model的信号
@receiver(post_save,sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    # 是否新建，因为update的时候也会进行post_save
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()
