from random import choice


from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler,jwt_payload_handler


from .models import Verifycode
from .serializers import SmsSerializer,UserRegSerializer,UserDetailSerializer
from utils.yunpian import YunPian
from DjangoDrf.settings import APIKEY




User = get_user_model() #取出user的moder
# Create your views here.

class CustomBackend(ModelBackend):
    """
    自定义用户验证 可以用手机登录
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    """
    发送短信验证码
    """

    serializer_class = SmsSerializer

    def generate_code(self):
        """
        随机生成手机验证码
        :return: code验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)



    #重写CreateModelMixin中的create方法,可以方便写自己的逻辑
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        #有效性验证失败会直接抛异常
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]

        yun_pian = YunPian(APIKEY)

        #生成随机验证码
        code = self.generate_code()

        #发送验证码
        sms_status = yun_pian.send_sms(code=code,mobile=mobile)

        #判断是否发送成功，成功返回0
        if sms_status["code"] != 0:
            return Response({
                "mobile":sms_status["msg"]
            },status=status.HTTP_400_BAD_REQUEST)

        else:
            #保存验证码
            code_record = Verifycode(code=code,mobile=mobile)
            code_record.save()
            return Response({
                "mobile":mobile
            },status=status.HTTP_201_CREATED)


class UserView(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    用户
    """

    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    #登录认证方法
    authentication_classes = (SessionAuthentication,JSONWebTokenAuthentication)



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        #返回Toke给前端,找到了生成token的两个重要步骤，一payload，二encode
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        #返回用户名
        re_dict["name"] = user.name if user.name else user.username


        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    #重载该方法,动态开启认证权限,返回一个列表
    def get_permissions(self):
        if self.action == "retrieve": #获取用户详情状态
            return [permissions.IsAuthenticated()]
        elif self.action == "create": #注册状态
            return []

        return [] #其它情况

    #重载该方法,动态序列化模型
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer



    #重载返回用户对象
    def perform_create(self, serializer):
        return serializer.save()

    #重写该方法，不管传什么id，都只返回当前用户,只合适viewset，mixins.RetrieveModelMixin，删除的时候
    def get_object(self):
        return self.request.user


