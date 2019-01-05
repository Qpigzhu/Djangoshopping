"""DjangoDrf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import path,include,re_path
from django.views.static import serve
import xadmin
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from .settings import MEDIA_ROOT
from goods.views import GoodsList,CategoryViewset,BannerViewset,IndexCategoryViewset
from users.views import SmsCodeView,UserView
from user_operation.views import UserFavView,LeavingMessageViewset,AddressViewset
from trade.views import ShoppingCartViewSet,OrderViewset,AlipayView

#使用router注册Url
router = DefaultRouter()
router.register('goods',GoodsList,base_name="GoodsList")

# 配置Category的url
router.register('categorys', CategoryViewset, base_name="categories")
#发送验证码
router.register("code",SmsCodeView,base_name="sms_code")

#用户
router.register("users",UserView,base_name="users")

#收藏
router.register("userfavs",UserFavView,base_name="userfavs")
#留言
router.register('messages', LeavingMessageViewset, base_name="messages")

#收货地址
router.register("address",AddressViewset,base_name="address")

#购物车
router.register(r'shopcarts', ShoppingCartViewSet, base_name="shopcarts")

# 订单相关url
router.register(r'orders', OrderViewset, base_name="orders")

#首页轮播图url
router.register("banners",BannerViewset,base_name="banners")

# 首页系列商品展示url
router.register(r'indexgoods', IndexCategoryViewset, base_name="indexgoods")
urlpatterns = [
    # path('admin/', admin.site.urls),

    #rest_framewor的Url,方便测试
    path('api-auth/', include('rest_framework.urls')),
    #xadmin后台Url
    path('xadmin/', xadmin.site.urls),
    # 富文本相关url
    path('ueditor/', include('DjangoUeditor.urls')),
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    re_path('media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),

    #rest_framework自动化文档,1.11版本中注意此处前往不要加$符号
    path('docs/',include_docs_urls(title='mtianyan生鲜超市文档')),

    #食品列表
    # path('goods/',GoodsList.as_view(),name="食品列表"),
    #使用router注册Url
    path('', include(router.urls)),

    #使用jwt来登录
    path('login/',obtain_jwt_token),

    #支付宝接口
    path("alipay/retrun",AlipayView.as_view(),name="alipay"),
    # 首页
    path('index/', TemplateView.as_view(template_name='index.html'))

]
