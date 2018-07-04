# -*- coding: utf-8 -*-
import re
import json
import logging

import scrapy
from scrapy.exceptions import CloseSpider

from mbcrawl.itemloaders import BeiBeiProductLoader, BeiBeiSkuLoader
from mbcrawl.items import BeibeiProduct, BeibeiSku


class BeibeiSpider(scrapy.Spider):
    name = 'beibei'
    allowed_domains = ['beibei.com']
    start_urls = ['http://global.beibei.com/']

    def parse(self, response):
        """
        parses the home page
        @url http://global.beibei.com/
        @returns requests 5 8
        """
        for cate_selector in response.css("div.sub-nav-cont ul li a"):
            link = cate_selector.css("::attr(href)").extract_first()
            if response.urljoin(link) in self.start_urls:
                continue
            cate_name = cate_selector.css("::attr(c-bname)").extract_first()
            meta = {"cate_name": cate_name, "page_num": 1,
                    "base_url": link.rsplit(".", 1)[0]}
            yield response.follow(link, callback=self.parse_category, meta=meta)

    def parse_category(self, response):
        """
        parses the category page which is a list of items
        @url http://global.beibei.com/category/pregent_nutrition.html
        @meta page_num 1
        @meta cate_name pregent_nutrition
        @meta base_url http://global.beibei.com/category/pregent_nutrition.html
        @returns_specific beibei_detail 40 80
        @returns_specific beibei_category_page
        """
        detail_links = response.css("a.detail-url-click::attr(href)").extract()
        meta = response.meta
        self.logger.info("found %s products from page %s of category %s",
                         len(detail_links), meta["page_num"], meta["cate_name"])
        for link in detail_links:
            if not link:
                continue
            yield response.follow(link, callback=self.parse_detail, meta=meta)
        if detail_links:
            meta = dict(meta)
            meta["page_num"] = int(meta["page_num"]) + 1
            base_url = meta["base_url"]
            link = "{}---hot-{}.html".format(base_url, meta["page_num"])
            self.logger.info("scheduled scraping request for page %s of category %s",
                             meta["page_num"], meta["cate_name"])
            yield response.follow(link, callback=self.parse_category, meta=meta)

    def parse_detail(self, response):
        """
        parse the product detail page.
        @url http://www.beibei.com/detail/p/1272418.html
        @meta cate_name pregent_nutrition
        @returns item 10 20
        """
        loader = BeiBeiProductLoader(BeibeiProduct(), response=response)
        match = re.search(r'/detail/p/([0-9]+)\.html',
                          response.url)
        if not match:
            self.logger.warn("product id not found from URL: %s", response.url)
            return
        product_id = int(match.group(1))
        loader.add_value("id", product_id)
        loader.add_css("name", "h3.over-title::text")
        loader.add_value("category", response.meta["cate_name"])
        loader.add_css("description", "p.over-memo::text")
        img_info = self.parse_images(response.text)
        for v in img_info.values():
            loader.add_value("file_urls", v)
        loader.add_value("img_info", img_info)
        yield loader.load_item()
        yield from self.parse_sku(product_id, response.text, img_info)

    def parse_images(self, resp_text):
        match = re.search(r"pageData\.itemImgs = '(.+)';", resp_text)
        if not match:
            return {}

        img_info = {}

        for line in json.loads(match.group(1)):
            attr_key, img_url = line.split(":", 1)
            img_info[attr_key] = img_url
        return img_info

    def parse_sku(self, product_id, resp_text, img_info):
        match = re.search(r"pageData\.sku_data = '(.+)';", resp_text)
        if not match:
            return

        sku_info = json.loads(match.group(1))
        attr_to_kind = {}
        for kind_code, attr_codes in sku_info.get("sku_id_map", {}).items():
            for attr_code in attr_codes:
                attr_to_kind[str(attr_code)] = kind_code
        attr_kind_names = sku_info.get("sku_kv_map", {})

        for sku_attr_comb, sku_obj in sku_info.get("sku_stock_map", {}).items():
            if not isinstance(sku_obj, dict) or "id" not in sku_obj:
                continue
            loader = BeiBeiSkuLoader(BeibeiSku())
            loader.add_value("id", sku_obj["id"])
            loader.add_value("product_id", product_id)
            loader.add_value("price", sku_obj.get("price"))
            loader.add_value("origin_price", sku_obj.get("origin_price"))
            loader.add_value("stock", sku_obj.get("stock"))

            for attr_code in re.split('v', sku_attr_comb):
                if not attr_code:
                    continue
                attr_name = attr_kind_names.get("v"+attr_code)
                kind_code = attr_to_kind.get(attr_code)
                if kind_code:
                    kind_name = attr_kind_names.get("k"+kind_code)
                else:
                    kind_name = ""
                loader.add_value("name", "{}:{}".format(kind_name, attr_name))
                if attr_code in img_info:
                    loader.add_value("img_sku_attr_code", attr_code)
            yield loader.load_item()
