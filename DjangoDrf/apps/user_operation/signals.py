# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2019\1\5 0005 11:33$'

"""
信号量
"""
from django.conf import settings
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import UserFav

#参数一接受哪种信号，参数二是接受哪个model的信号
@receiver(post_save,sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    # 是否新建，因为update的时候也会进行post_save
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(post_delete,sender=UserFav)
def delete_userfav(sender, instance=None, created=False, **kwargs):
    # 是否删除，因为删除的时候也会进行post_delete
    goods = instance.goods
    goods.fav_num -= 1
    goods.save()

