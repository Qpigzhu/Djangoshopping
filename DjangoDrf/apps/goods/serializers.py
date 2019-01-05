# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\10\20 0020 13:38$'

from rest_framework import serializers
from django.db.models import Q
from .models import Goods,GoodsCategory,GoodsImage,Banner,GoodsCategoryBrand,IndexAd

#绑定models的数据
# class GoodsSerializers(serializers.Serializer):
#     name = serializers.CharField(required=True,max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()

#使用ModelSerializer绑定数据

#使得外键可以显示

#三级分类
class GoodsCategorySerializers3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


#两级分类
class GoodsCategorySerializers2(serializers.ModelSerializer):
    sub_cat = GoodsCategorySerializers3(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"




#进行Serializer的嵌套使用。覆盖外键字段
#一级分类
class GoodsCategorySerializers(serializers.ModelSerializer):
    sub_cat = GoodsCategorySerializers2(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image",)


class GoodsSerializers(serializers.ModelSerializer):
    category = GoodsCategorySerializers()   #进行Serializer的嵌套使用。覆盖外键字段
    #有多条的时候，需要加many=True
    images = GoodsImageSerializers(many=True)
    class Meta:
        model = Goods
        fields = "__all__"

class BannerSerirlizers(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"

#品牌序列化
class BrandSerirlizers(serializers.ModelSerializer):
     class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexCategorySerirlizer(serializers.ModelSerializer):
    # 一个category会有多个brand。
    brands = BrandSerirlizers(many=True)
    #外键指向的第三类。而我们要拿到第一类别的数据。直接使用goods的Serializer取不出来。
    goods  = serializers.SerializerMethodField()
    #取到二级商品分类
    sub_cat = GoodsCategorySerializers2(many=True)
    #首页商品类别广告
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self,obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id, )
        if ad_goods:
            good_ins = ad_goods[0].goods
            goods_json = GoodsSerializers(good_ins, many=False, context={'request': self.context['request']}).data
        return goods_json


    def get_goods(self,obj):
        # 将这个商品相关父类子类等都可以进行匹配
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(
            category__parent_category__parent_category_id=obj.id))
        goods_serializer = GoodsSerializers(all_goods,many=True,context={"request":self.context["request"]})
        return goods_serializer.data


    class Meta:
        model = GoodsCategory
        fields = "__all__"