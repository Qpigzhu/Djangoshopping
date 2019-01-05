from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from utils.permissions import IsOwnerOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .models import UserFav,UserLeavingMessage,UserAddress
from .serializers import UserFavSerializers,UserFavDetailSerializer,UserLeavingMessageSerializers,AddressSerializer

# Create your views here.


class UserFavView(mixins.CreateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
        list:
            获取用户收藏
        create:
            添加收藏
        delete:
            删除收藏
        retrieve:
            判断某个商品是否收藏
    """
    #queryset = UserFav.objects.all()
    #用户权限认证,IsAuthenticated判断是否登录,IsOwnerOrReadOnly判断是否当前用户
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)
    #serializer_class = UserFavSerializers
    #用户验证
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)
    lookup_field = "goods_id"

    #重载列表方法,显示当前用户的收藏
    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    #动态序列化
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
            return UserFavSerializers
        return UserFavSerializers


class LeavingMessageViewset(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    """
        list:
            获取用户留言
        create:
            添加留言
        delete:
            删除留言
    """
    serializer_class = UserLeavingMessageSerializers

    #登录认证
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)
    #权限认证
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)

    #返回当前用户的留言
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class AddressViewset(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收货地址
    create:
        添加收货地址
    update:
        更新收货地址
    delete:
        删除收货地址
    """
    serializer_class = AddressSerializer
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)
    permission_classes = (IsOwnerOrReadOnly,IsAuthenticated)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)



