import unittest
import pkg_resources

from scrapy.http import Request, TextResponse
from mbcrawl.spiders.beibei import BeibeiSpider
from mbcrawl.items import BeibeiProduct, BeibeiSku


class TestBeiBeiParsing(unittest.TestCase):

    def setUp(self):
        self.spider = BeibeiSpider("beibei")

    def mkresp(self, url, filename, meta=None):
        content = pkg_resources.resource_string(__name__, filename)
        return TextResponse(
            url=url, body=content, request=Request(url, meta=meta))

    def test_parse(self):
        resp = self.mkresp("http://global.beibei.com/", "index.html")
        req_or_items = list(self.spider.parse(resp))
        self.assertEqual(6, len(req_or_items))
        for req in req_or_items:
            self.assertIsInstance(req, Request)

        first_req = req_or_items[0]
        self.assertEqual(
            "http://global.beibei.com/category/babythings_diaper.html", first_req.url)
        meta = first_req.meta
        self.assertEqual(
            "http://global.beibei.com/category/babythings_diaper", meta["base_url"])
        self.assertEqual(1, meta["page_num"])
        self.assertEqual("自营纸尿裤", meta["cate_name"])

    def test_parse_category(self):
        meta = {
            "page_num": 1,
            "cate_name": "母婴营养辅食",
            "base_url": "http://global.beibei.com/category/pregent_nutrition"
        }
        resp = self.mkresp(
            "http://global.beibei.com/category/pregent_nutrition.html",
            "pregent_nutrition.html",
            meta)
        req_or_items = list(self.spider.parse_category(resp))
        self.assertEqual(69, len(req_or_items))
        first_item_req = req_or_items[0]
        self.assertEqual(
            "http://www.beibei.com/detail/p/1272418.html", first_item_req.url)
        self.assertEqual(meta, first_item_req.meta)

        next_page_req = req_or_items[-1]

        self.assertEqual(
            "http://global.beibei.com/category/pregent_nutrition---hot-{}.html".format(
                meta["page_num"]+1),
            next_page_req.url)
        exp_next_page_meta = dict(meta)
        exp_next_page_meta["page_num"] = meta["page_num"] + 1
        self.assertEqual(exp_next_page_meta, next_page_req.meta)

        empty_resp = self.mkresp(
            "http://global.beibei.com/category/pregent_nutrition---hot-58.html",
            "pregent_nutrition_empty.html", meta)
        req_or_items = list(self.spider.parse_category(empty_resp))
        self.assertEqual(0, len(req_or_items))

    def test_parse_detail(self):
        meta = {"cate_name": "美妆个护"}
        resp = self.mkresp(
            "http://www.beibei.com/detail/p/1940750.html", "detail.html", meta)
        req_or_items = list(self.spider.parse_detail(resp))
        self.assertEqual(8, len(req_or_items))
        product = req_or_items[0]
        skus = req_or_items[1:]
        self.assertIsInstance(product, BeibeiProduct)
        for sku in skus:
            self.assertIsInstance(sku, BeibeiSku)

        self.assertEqual(1940750, product["id"])
        self.assertEqual(
            'Innisfree/悦诗风吟\xa0【包邮包税】眉笔防水防汗不脱色持久眉粉染眉膏一字眉初学者  0.3', product["name"])
        self.assertEqual("美妆个护", product["category"])
        self.assertEqual(
            "扁平状笔头，无论是平刷还是描边均可适用，让你的眉毛富有立体感，"
            "色彩鲜明，上色自然，不会很浓很明显，多次上色，即可勾画出漂亮眉型。"
            "一端是眉笔，可描画双眉；另一端是眉刷，用于整理眉型，方便贴心。", product["description"])
        self.assertEqual(7, len(product["file_urls"]))
        self.assertEqual(
            "http://b1.hucdn.com/upload/item/1609/22/25564813256560_800x800.jpg", product["file_urls"][0])
        self.assertEqual(
            "http://b1.hucdn.com/upload/item/1609/22/25562253456560_800x800.jpg", product["file_urls"][-1])
        self.assertEqual(7, len(product["img_info"]))
        self.assertEqual(
            "http://b1.hucdn.com/upload/item/1609/22/25564813256560_800x800.jpg", product["img_info"]["15"])

        first_sku = skus[0]
        self.assertEqual(62267326, first_sku["id"])
        self.assertEqual(product["id"], first_sku["product_id"])
        self.assertEqual("颜色:06# 蜜棕色", first_sku["name"])
        self.assertEqual(8600, first_sku["origin_price"])
        self.assertEqual(2600, first_sku["price"])
        self.assertEqual(0, first_sku["stock"])
