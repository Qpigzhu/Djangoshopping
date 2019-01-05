# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\12\6 0006 10:42$'
import re
from datetime import datetime,timedelta

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator #检查字段的唯一性

from DjangoDrf.settings import REGEX_MOBILE
from .models import Verifycode

User = get_user_model()


#序列化验证码模型
class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)


    def validate_mobile(self, mobile):
        """
        验证手机号码(函数名称必须为validate_ + 字段名)
        """

        #手机是否被注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("手机号码已被注册")


        #验证手机号码是否合法
        if not re.match(REGEX_MOBILE,mobile):
            raise serializers.ValidationError("手机号码非法")


        #验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0,minutes=1,seconds=0)

        # 添加时间大于一分钟以前。也就是距离现在还不足一分钟
        if Verifycode.objects.filter(add_time__gt=one_mintes_ago,mobile=mobile):
            raise serializers.ValidationError("距离上一次发送未超过60s")


        return mobile



#用户信息详情
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "gender", "birthday", "email","mobile")



#用户注册
class UserRegSerializer(serializers.ModelSerializer):
    #定义验证码字段,write_onle只写，不可以读的状态
    #code字段添加write_only = true。就不会将此字段进行序列化返回给前端。
    code = serializers.CharField(min_length=4,max_length=4,write_only=True,error_messages={
        "blank":"请输入验证码", #为空时的错误
        "required":"请输入验证码", #为空时的错误
        "max_length":"验证码格式错误",
        "min_length":"验证码格式错误",
    },help_text="验证码")

    #检查用户是否存在,UniqueValidator检查是否的唯一性,validators自定义过滤规则
    username = serializers.CharField(label="用户名",help_text="用户名",required=True,allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(),message="用户已经存在")])


    #style能使用密码输入框
    #password字段添加write_only = true。就不会将此字段进行序列化返回给前端。
    password = serializers.CharField(
        style={"input_type": "password",},label="密码",help_text="密码",write_only=True
    )

    # 调用父类的create方法，该方法会返回当前model的实例化对象即user。
    # 前面是将父类原有的create进行执行，后面是加入自己的逻辑
    # def create(self, validated_data):
    #     user = super(UserRegSerializer, self).create(validated_data=validated_data)
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user


    #在Serializer中添加code字段，这个code是多余字段不会被保存到数据库中
    def validated_code(self,code):
        # 验证码在数据库中是否存在，用户从前端post过来的值都会放入initial_data里面，排序(最新一条)。
        verify_records = Verifycode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            #取得最新一条验证码
            last_record = verify_records[0]

            #有效期为五分钟
            five_mintes_ago = datetime.now() - timedelta(hours=0,minutes=5,seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")

        else:
            raise serializers.ValidationError("验证码错误")

    # 不加字段名的验证器作用于所有字段之上。attrs是字段 validate之后返回的总的dict
    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs


    #序列化User模型
    class Meta:
        model = User
        fields = ("username", "code", "mobile","password")

