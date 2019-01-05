# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\12\19 0019 10:06$'
import time
from random import Random

from rest_framework import serializers
from .models import ShoppingCart
from goods.serializers import GoodsSerializers
from goods.models import Goods
from .models import OrderGoods,OrderInfo

from utils.alipay import AliPay
from DjangoDrf.settings import private_key_path,ali_pub_key_path,alipay_appid

#购物车列表详情
class ShoppingCartDatilSerializers(serializers.ModelSerializer):
    # 一条购物车关系记录对应的只有一个goods。
    goods = GoodsSerializers(many=False,read_only=True)
    class Meta:
        model = ShoppingCart
        fields = ("goods","nums")




#序列化商品
class OrderGoodsSerialzier(serializers.ModelSerializer):
    goods = GoodsSerializers(many=False)
    class Meta:
        model = OrderGoods
        fields = "__all__"

#反向查询订单有多少商品序列化
class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerialzier(many=True)

    # Serializer中加一个字段alipay_url 专门返回支付宝的支付链接。
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # obj是OrderInfo的模型
    def get_alipay_url(self, obj):
        alipay = AliPay(
            appid="2016092300579459",
            app_notify_url="http://127.0.0.1:8000/alipay/retrun",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/retrun"
        )
        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )

        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url
    class Meta:
        model = OrderInfo
        fields = "__all__"



# 使用Serializer本身最好, 因为它是灵活性最高的。
#购物车
class ShoppingCartSerializers(serializers.Serializer):
    #获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(min_value=1,label="数量",required=True,error_messages={
        "min_value":"数量至少为1",
        "required":"不能为空"
    })

    goods = serializers.PrimaryKeyRelatedField(required=True,queryset=Goods.objects.all())

    #Serializer是没有提供save功能的，所以我们要来重写create方法
    def create(self, validated_data):
        #获取用户
        user = self.context["request"].user
        nums = self.validated_data["nums"]
        goods = self.validated_data["goods"]

        #查看是否已加入购物车
        existed = ShoppingCart.objects.filter(user=user,goods=goods)
        #已加入时,数量加1
        if existed:
            existed = existed[0]
            existed.nums += 1
            existed.save()
        #否则创建对象
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    #Serializer继承于baseSerializer。但是Serializer并没有去重写update方法。
    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


#订单
class OrderInfoSerializers(serializers.ModelSerializer):
    #获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    order_sn = serializers.CharField(read_only=True)
    nonce_str = serializers.CharField(read_only=True)
    pay_status = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M")
    trade_no = serializers.CharField(read_only=True)

    #Serializer中加一个字段alipay_url 专门返回支付宝的支付链接。
    alipay_url = serializers.SerializerMethodField(read_only=True)

    #obj是OrderInfo的模型
    def get_alipay_url(self,obj):
        alipay = AliPay(
            appid="2016092300579459",
            app_notify_url="http://127.0.0.1:8000/alipay/retrun",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/retrun"
        )
        url = alipay.direct_pay(
            subject=obj.order_sn, #订单名字
            out_trade_no=obj.order_sn,  #订单号
            total_amount=obj.order_mount,   #订单金额
        )

        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url

    #生成随机单号
    def generate_order_sn(self):
        # 当前时间+userid+随机数
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10,99))
        return order_sn

    #把随机订单号放进订单对象
    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"