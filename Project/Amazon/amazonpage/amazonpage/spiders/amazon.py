"""
需求:
1.打开首页切换英文首页(配送地址改为10001)
2.输入目标商品名称
3.获取20页的目标商品的ASIN
4.将获取的到ASIN的详情页详情页信息提取

可优化:
1.可变关键字参数增加title识别功能，不爬取特定词语的货物。形式: {title:[]}
2.可变关键字参数增加额外的爬取项。形式: { demo : { name1 :'css/xpath' , name2 : 'css/xpath'}}
"""
import copy

import scrapy
from scrapy import Request, Spider
import re
from amazonpage.items import AsinItem
import datetime


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['www.amazon.com']
    base_url = 'https://www.amazon.com'

    def start_requests(self):
        start_url = f'{self.base_url}/s?k=Disposable+Face+Mask&language=en_US'
        yield Request(start_url, callback=self.parse_index)

    def parse_index(self, response):
        for i in range(2, 21):
            asins_divs = response.xpath('//span[@data-component-type="s-search-results"]')
            asins_div = asins_divs.xpath('//div[@data-asin]')
            for div in asins_div:
                asin = div.xpath('./@data-asin').get()
                if asin:
                    detail_url = f'{self.base_url}/dp/{asin}?language=en_US'
                    if div.xpath('./data-component-type').get() == "s-search-result":
                        asin_to_type = {'asin_type': 'search', 'asin': asin}
                    else:
                        asin_to_type = {'asin_type': 'sponsored', 'asin': asin}
                    yield Request(detail_url, callback=self.parse_asin_detail, meta=asin_to_type, priority=2)

            next_url = f'{self.base_url}/s?k=Disposable+Face+Mask&page={i}&language=en_US'
            yield Request(next_url, callback=self.parse_index)
        # detail_url = f'{self.base_url}/dp/B09FJFHYCW?language=en_US'
        # asin_to_type = {'asin_type': 'search', 'asin': 'B08YPGJB4P'}
        # yield Request(detail_url, callback=self.parse_asin_detail, meta=asin_to_type, priority=2)

    def parse_asin_detail(self, response):

        # 获取品牌，标题，卖家，物流，A+，记录日期，商品类型
        asin = response.meta['asin']
        brand = response.xpath('//a[@id="bylineInfo"]/text()').re_first(
            r'Brand:\s(.*)|Visit\s?the\s?(.*)\s?Store').strip()
        title = response.xpath('//span[@id="productTitle"]/text()').get().strip()
        sold_by = response.xpath('//a[id="sellerProfileTriggerId"]/text()').get()
        fulfillment = response.xpath('//*[@id="tabular-buybox"]/div[1]/div[2]/div/span/text()').get()
        a_goods = "True" if response.xpath("//div[@id='aplus']//img") else "False"

        record_date = datetime.date.today().strftime('%Y-%m-%d')
        product_type = "KN95" if re.findall("KN95", title, re.I) else "N95" if re.findall("N95", title,
                                                                                          re.I) else "Normal"
        asin_type = response.meta['asin_type']

        # 获取价格，数量，颜色。并计算每个的价格
        asin_details = response.xpath('//div[@id="poExpander"]/div[1]//td//text()')
        for index, info in enumerate(asin_details.getall()):
            if info == 'Color':
                color = asin_details[index + 3].get()
                break
        else:
            color = None
        price = response.xpath(
            '//div[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[1]/text()').get() or response.xpath(
            '//div[@id="corePrice_desktop"]/div/table/tbody/tr[2]/td[2]/span[1]/span[1]/text()').get() or response.xpath(
            '//div[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]/span[1]/text').get()
        pcs_box = asin_details.re_first(r'([0-9]*)\sCount')
        if price and pcs_box:
            price_count = round(float(price.replace("$", "")) / float(pcs_box), 2)
        else:
            price_count = None

        # 获取上架日期
        product_details = response.xpath('//div[@id="detailBullets_feature_div"]//li//text()')
        lauched_date = ' '.join(product_details.re(r'([a-zA-Z]+)\s*([0-9]{1,2}),\s*([0-9]{4})'))

        # 获取大小分类与排名
        product_rank_string = ' '.join(
            response.xpath('//div[@id="detailBulletsWrapper_feature_div"]/ul[1]//span//text()').getall()).strip()
        # print(f'product_ranks', product_ranks)
        result = re.findall(r'#([0-9]+)\sin\s([a-zA-Z&\'\s]*)', product_rank_string, re.S)
        bsr = int(str(result[0][0]).replace(',', ''))
        category = result[0][1].strip()
        ranking = int(str(result[1][0]).replace(',', ''))
        subcategory = result[1][1].strip()

        # listing = re.findall(r'"parentAsin=(.*)&|parentAsin":"(.*)",', str(response.body), re.S)
        # print(listing)
        # print()

        item = AsinItem()
        item['asin'] = asin
        item['brand'] = brand
        item['title'] = title
        item['sold_by'] = sold_by
        item['fulfillment'] = fulfillment
        item['a_goods'] = a_goods
        item['record_date'] = record_date
        item['product_type'] = product_type
        item['asin_type'] = asin_type
        item['color'] = color
        item['price'] = price
        item['pcs_box'] = pcs_box
        item['price_count'] = price_count
        item['lauched_date'] = lauched_date
        item['bsr'] = bsr
        item['category'] = category
        item['ranking'] = ranking
        item['subcategory'] = subcategory

        review_url = response.xpath('//div[@id="reviews-medley-footer"]/div[2]/a/@href').get()
        yield Request(f'{self.base_url}{review_url}&language=en_US', callback=self.parse_review_detail,
                      meta={'item': copy.deepcopy(item)})

        # seller_url = response.xpath('//a[id="sellerProfileTriggerId"]/@href')
        # yield Request(self.base_url + seller_url, callback=self.parse_seller_detail, meta={'item': copy.deepcopy(item)})

    def parse_review_detail(self, response):
        product_reviews = response.xpath('//div[@id="filter-info-section"]/div/text()').re(r'[0-9,]*,?[0-9]{1,3}')
        rating = int(str(product_reviews[0]).replace(',', ''))
        review = int(str(product_reviews[1]).replace(',', ''))
        star = response.xpath(
            '//div[@id="cm_cr-product_info"]/div/div[1]/div[2]/div/div/div[2]/div/span/text()').re_first(r'[0-9.]*')
        _item = response.meta['item']
        _item['rating'] = rating
        _item['review'] = review
        _item['star'] = star
        item = AsinItem(_item)
        yield item

    # def parse_seller_detail(self, response):
    #     business_name = response.xpath('//div[@id="page-section-detail-seller-info"]/div/div/div/div[2]/text()').get()
    #     address = response.xpath('')
    #     province_country = response
    #     origin = response
