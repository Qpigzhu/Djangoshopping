# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\12\16 0016 20:48$'

import re

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import UserFav,UserLeavingMessage,UserAddress
from DjangoDrf.settings import REGEX_MOBILE
from goods.serializers import GoodsSerializers



class UserFavDetailSerializer(serializers.ModelSerializer):
    # 通过goods_id拿到商品信息。就需要嵌套的Serializer
        goods = GoodsSerializers()
        class Meta:
            model = UserFav
            fields = ("goods", "id")


class UserFavSerializers(serializers.ModelSerializer):
    #获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )


    class Meta:
        model = UserFav
        # 使用validate方式实现唯一联合
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏"
            )
        ]
        fields = ("user","goods","id")


class UserLeavingMessageSerializers(serializers.ModelSerializer):
    #获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    #read_only自动获取时间，只读状态，不可写
    add_time = serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ("user","message_type","subject","message","file","add_time","id")


#收货地址
class AddressSerializer(serializers.ModelSerializer):
    #手机验证
    signer_mobile = serializers.CharField(max_length=11,min_length=11,error_messages={
        "max_length":"手机至多11位",
        "min_length":"手机至少11位"
    },help_text="手机号码")
    signer_name = serializers.CharField(required=True,error_messages={
        "blank":"联系人不能为空",
        "required":"联系人不能为空",
    },help_text="联系人")

    # 验证手机号码是否合法
    def validate_signer_mobile(self,signer_mobile):
        if not re.match(REGEX_MOBILE,signer_mobile):
            raise serializers.ValidationError("手机非法")
        return signer_mobile



    #获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    #获取当前时间
    add_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserAddress
        fields = ("id", "user", "province", "city", "district", "address", "signer_name", "add_time", "signer_mobile")