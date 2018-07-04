import re

from scrapy.http import Request

from . import SpecificResultChecker
import mbcrawl.contracts.beibei


class BeiBeiReturnsDetailChecker(SpecificResultChecker):
    result_name = "beibei_detail"
    url_pattern = re.compile(
        r"http://www.beibei.com/detail/p/[0-9]+.html"
    )

    def check_match(self, output_item):
        return isinstance(output_item, Request)\
            and self.url_pattern.match(output_item.url)


class BeiBeiReturnsCategoryPageChecker(SpecificResultChecker):
    result_name = "beibei_category_page"

    url_pattern = re.compile(
        r'http://global.beibei.com/category/[^/]+---hot-[0-9]+.html')

    def check_match(self, output_item):
        return isinstance(output_item, Request)\
            and self.url_pattern.match(output_item.url)
