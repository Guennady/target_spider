import jmespath
import json
import scrapy
import six


class Product(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    image_urls = scrapy.Field()


class TargetSpider(scrapy.Spider):
    """Scraps target.com for Easter Easter Peanut Butter Eggs"""
    name = 'target_spider'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                      'AppleWebKit/537.36 (KHTML like Gecko)'
                      'Chrome/78.0.3904.87 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'connection': 'keep-alive',
            'accept': 'text/html,application/xthml+xml,application/xml;q=0.9,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'upgrade-insecure-requests': '1'
        }
    }

    start_urls = [
        'https://redsky.target.com/redsky_aggregations/v1/web/'
        'pdp_client_v1?key=ff457966e64d5e877fdbad070f276d18ecec4a01'
        '&tcin=53957905&store_id=none&has_store_id=false'
        '&pricing_store_id=3991&scheduled_delivery_store_id=none'
        '&has_scheduled_delivery_store_id=false&has_financing_options=false',
    ]

    def parse(self, response):
        item = Product()
        json_resp = json.loads(response.text)

        title_path = 'data.product.item.product_description.title'
        title = jmespath.search(title_path, json_resp)
        item['title'] = title.replace('&#39;', "'") if isinstance(title, six.string_types) else title

        descr_path = 'data.product.item.product_description.downstream_description'
        item['description'] = jmespath.search(descr_path, json_resp)

        price_path = 'data.product.price.formatted_current_price'
        item['price'] = jmespath.search(price_path, json_resp)

        prim_image_path = 'data.product.item.enrichment.images.primary_image_url'
        prim_image_url = jmespath.search(prim_image_path, json_resp)

        alt_image_path = 'data.product.item.enrichment.images.alternate_image_urls'
        alt_image_urls = jmespath.search(alt_image_path, json_resp)

        item['image_urls'] = [prim_image_url] + alt_image_urls if prim_image_url else alt_image_urls

        yield item

