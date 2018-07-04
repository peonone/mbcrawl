import unittest
from collections import OrderedDict

from mbcrawl.itemloaders import ProductLoader, SkuLoader
from mbcrawl.items import Product, Sku, BeibeiProduct


class TestItemLoader(unittest.TestCase):
    def test_product_itemloader(self):
        loader = ProductLoader(Product())
        loader.add_value("id", 333222)
        loader.add_value("name", "x"*1000)
        loader.add_value("description", "y"*2000)
        loader.add_value("file_urls", "http://url1.com/")
        loader.add_value("file_urls", "http://url2.com/path/to")
        item = loader.load_item()

        self.assertEqual(333222, item["id"])
        self.assertEqual("x"*512, item["name"])
        self.assertEqual("y"*1024, item["description"])
        self.assertEqual(
            ["http://url1.com/", "http://url2.com/path/to"],
            item["file_urls"])

    def test_sku_itemloader(self):
        loader = SkuLoader(Sku())
        loader.add_value("product_id", 333222)
        loader.add_value("name", "part1")
        loader.add_value("name", "part2")
        loader.add_value("name", "x"*1024)

        item = loader.load_item()
        self.assertEqual(333222, item["product_id"])
        self.assertEqual("part1 part2 " + "x"*500, item["name"])


class TestBeiBeiSkuImages(unittest.TestCase):
    def test_sku_images(self):
        product = BeibeiProduct()
        img_url1 = "http://example.com/path/to/1.jpg"
        img_url2 = "http://example.com/path/to/2.jpg"

        uploaded_path1 = "/path/to/abc1.jpg"
        uploaded_path2 = "/path/to/abc2.jpg"
        product["id"] = 12345
        product["files"] = [{"url": img_url1, "path": uploaded_path1}, {
            "url": img_url2, "path": uploaded_path2}]
        product["img_info"] = {
            "15": img_url1,
            "344": img_url2
        }
        table, rows = product.db_helper_table_rows()
        self.assertEqual("sku_images_beibei", table)
        exp_rows = [
            {
                "product_id": 12345,
                "sku_attr_code": "15",
                "uploaded_path": uploaded_path1
            },
            {
                "product_id": 12345,
                "sku_attr_code": "344",
                "uploaded_path": uploaded_path2
            }
        ]
        self.assertEqual(exp_rows, sorted(
            rows, key=lambda x: x["sku_attr_code"]))
