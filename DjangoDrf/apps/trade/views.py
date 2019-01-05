import datetime


from django.shortcuts import render,redirect
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from utils.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response



from .serializers import ShoppingCartSerializers,ShoppingCartDatilSerializers,OrderInfoSerializers,OrderDetailSerializer
from .models import ShoppingCart,OrderInfo,OrderGoods
from utils.alipay import AliPay
from DjangoDrf.settings import private_key_path,ali_pub_key_path,alipay_appid
# Create your views here.



class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
        list:
            获取购物车详情
        create：
            加入购物车
        delete：
            删除购物记录
        """
    # serializer_class = ShoppingCartSerializers
    # queryset = ShoppingCart.objects.all()
    authentication_classes = (SessionAuthentication,JSONWebTokenAuthentication)
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)

    lookup_field ="goods_id"

    #动态序列化,现在的Serializer里面只有goods的主键id。需要动态的设置Serializer
    def get_serializer_class(self):
        if self.action == "list":
            return ShoppingCartDatilSerializers
        else:
            return ShoppingCartSerializers

    #获取当前用户的购物车
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)



class OrderViewset(mixins.ListModelMixin,mixins.DestroyModelMixin,mixins.CreateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
        订单管理
        list:
            获取个人订单
        delete:
            删除订单
        create：
            新增订单
        """
    serializer_class = OrderInfoSerializers
    authentication_classes = (SessionAuthentication,JSONWebTokenAuthentication)
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)

    #在validate中做了之后，在view中就可以直接调用save了
    def perform_create(self, serializer):
        order = serializer.save()

        # 获取到用户购物车里的商品
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()

            shop_cart.delete()

        return order
    #动态开启序列化
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderInfoSerializers


    #获取当前用户的购物车
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)


class AlipayView(APIView):
    def get(self,request):
        """
        处理支付宝的retrun_url返回
        :param request:
        :return:
        """
        # 1. 先将sign剔除掉
        processed_dict = {}
        for key,value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sing",None)

        # 2. 生成一个Alipay对象

        alipay = AliPay(
            appid=alipay_appid,
            app_notify_url="http://127.0.0.1:8000/alipay/retrun",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/retrun"
        )

        # 3. 进行验签，确保这是支付宝给我们的
        verify_re = alipay.verify(processed_dict,sign)
        # 如果验签成功
        if verify_re is True:
            #商家订单号
            order_sn = processed_dict.get("out_trade_no",None)
            #支付宝支付订单号
            trade_no = processed_dict.get("trade_no",None)
            #支付状态
            trade_status = processed_dict.get('trade_status', None)

            # 查询数据库中存在的订单
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)

            for existed_order in existed_orders:
                # 订单商品项
                order_goods =  existed_order.goods.all()

                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                # 更新订单状态，填充支付宝给的交易凭证号。
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            response = redirect("index")
            # 希望跳转到vue项目的时候直接帮我们跳转到支付的页面
            response.set_cookie("nextPath","pay",max_age=2)
            return response
        else:
            response = redirect("index")
            return response

    def post(self,request):
        """
        处理支付宝的notify_url
        :param request:
        :return:
        """
        # 1. 先将sign剔除掉
        processed_dict = {}
        for key,value in request.POST.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sing",None)

        # 2. 生成一个Alipay对象

        alipay = AliPay(
            appid=alipay_appid,
            app_notify_url="http://127.0.0.1:8000/alipay/retrun",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/retrun"
        )

        # 3. 进行验签，确保这是支付宝给我们的
        verify_re = alipay.verify(processed_dict,sign)
        # 如果验签成功
        if verify_re is True:
            #商家订单号
            order_sn = processed_dict.get("out_trade_no",None)
            #支付宝支付订单号
            trade_no = processed_dict.get("trade_no",None)
            #支付状态
            trade_status = processed_dict.get('trade_status', None)

            # 查询数据库中存在的订单
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)

            for existed_order in existed_orders:
                # 订单商品项
                order_goods =  existed_order.goods.all()

                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                # 更新订单状态，填充支付宝给的交易凭证号。
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            # 将success返回给支付宝，支付宝就不会一直不停的继续发消息了。
            return Response("success")