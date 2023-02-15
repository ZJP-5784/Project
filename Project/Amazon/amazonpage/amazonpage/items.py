# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class AmazonpageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AsinItem(Item):
    asin = Field()  # ASIN
    brand = Field()  # 品牌
    # seller = Field()  # 卖家
    title = Field()  # 标题
    sold_by = Field()  # 销售方
    fulfillment = Field()  # 物流方式
    category = Field()  # 大类目
    subcategory = Field()  # 小类别
    rating = Field()  # 评级人数
    review = Field()  # Q&A数量
    star = Field()  # 星级
    bsr = Field()  # 大类目排名
    ranking = Field()  # 小类别排名
    # listing = Field()  # 母ASIN
    a_goods = Field()  # 是否A+
    price = Field()  # 价格
    # price_range = Field()  # 价格区间
    pcs_box = Field()  # 数量/每盒
    price_count = Field()  # 单价
    # si_month = Field()  # 每月销量
    # daily_si = Field()  # 每日销量
    # gmv_month = Field()  # 每月销售额
    lauched_date = Field()  # 上架日期
    record_date = Field()  # 数据记录日期
    business_name = Field()  # 商家名称
    address = Field()  # 商家地址
    province_country = Field()  # 商家所在地/城市
    origin = Field()  # 商家所在国家
    product_type = Field()  # 商品类型
    color = Field()  # 颜色
    # status = Field()  # 商品状态
    asin_type = Field()  # 产品状态
