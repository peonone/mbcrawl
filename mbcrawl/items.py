# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    db_skip_fields = ["file_urls", "files"]

    id = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class Sku(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    product_id = scrapy.Field()
    price = scrapy.Field()
    origin_price = scrapy.Field()
    stock = scrapy.Field()


class BeibeiProduct(Product):
    db_table = 'products_beibei'
    db_skip_fields = list(Product.db_skip_fields)
    db_skip_fields.append("img_info")

    sku_imgs_table = "sku_images_beibei"

    img_info = scrapy.Field()

    def db_helper_table_rows(self):
        rows = []
        files_dict = {r["url"]: r["path"] for r in self["files"]}
        for sku_attr_code, url in self["img_info"].items():
            if url in files_dict:
                rows.append(
                    {
                        "product_id": self["id"],
                        "sku_attr_code": sku_attr_code,
                        "uploaded_path": files_dict[url]
                    }
                )
        return self.sku_imgs_table, rows


class BeibeiSku(Sku):
    db_table = 'skus_beibei'
    img_sku_attr_code = scrapy.Field()
