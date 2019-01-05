# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2018\10\20 0020 17:00$'
from django.db.models import Q
from django_filters import rest_framework as filters
from goods.models import Goods


class GoodsFilter(filters.FilterSet):
    #name代表过滤的字段,lookup_expr代表过滤的条件,相当于Goods.objects.filter(shop_price__get=price_min)
    pricemin = filters.NumberFilter(name='shop_price', lookup_expr='gte')
    pricemax = filters.NumberFilter(name='shop_price', lookup_expr='lte')

    #自定义过滤方法
    top_category = filters.NumberFilter(name="category", method='top_category_filter')
    def top_category_filter(self, queryset, name, value):
        # 不管当前点击的是一级目录二级目录还是三级目录。
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(
            category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin','pricemax','category','is_hot','is_new']