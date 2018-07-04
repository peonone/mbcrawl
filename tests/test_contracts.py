from unittest import TextTestResult

from twisted.trial import unittest
from scrapy.spiders import Spider
from scrapy import Request
from scrapy.contracts import ContractsManager
from scrapy.contracts.default import (
    UrlContract,
    ReturnsContract,
    ScrapesContract
)

from mbcrawl.contracts import MetaContract, SpecificReturnsContract


class TestBeibeiSpider(Spider):
    name = "beibei"

    def set_meta(self, response):
        """
        @url http://global.beibei.com/
        @meta metakey1 metaval1
        @meta metakey2 metaval2
        @returns_specific beibei_detail 1 1
        """
        return Request(url="http://www.beibei.com/detail/p/123456.html")

    def returns_detail_ok(self, response):
        """
        @url http://global.beibei.com/
        @returns_specific beibei_detail
        """
        return Request(url="http://www.beibei.com/detail/p/123456.html")

    def returns_detail_fail(self, response):
        """
        @url http://global.beibei.com/
        @returns_specific beibei_detail 0 0
        """
        return Request(url="http://www.beibei.com/detail/p/123456.html")

    def returns_detail_category_ok(self, response):
        """
        @url http://global.beibei.com/
        @returns_specific beibei_detail 1 2
        @returns_specific beibei_category_page 1
        """
        yield Request(url="http://www.beibei.com/detail/p/123456.html")
        yield Request(url="http://www.beibei.com/detail/p/123456.html")
        yield Request(url="http://global.beibei.com/category/xxx----hot-1.html")

    def returns_detail_category_fail(self, response):
        """
        @url http://global.beibei.com/
        @returns_specific beibei_detail 1 2
        @returns_specific beibei_category_page 1
        """
        yield Request(url="http://www.beibei.com/detail/p/123456.html")
        yield Request(url="http://global.beibei.com/category/xxx.html")


class ResponseMock(object):
    url = 'http://global.beibei.com'


class CustomContractsTest(unittest.TestCase):
    contracts = [UrlContract, MetaContract,
                 ReturnsContract, SpecificReturnsContract,
                 ScrapesContract]

    def setUp(self):
        self.spider = TestBeibeiSpider()
        self.conman = ContractsManager(self.contracts)
        self.results = TextTestResult(
            stream=None, descriptions=False, verbosity=0)

    def should_succeed(self):
        self.assertFalse(self.results.failures)
        self.assertFalse(self.results.errors)

    def should_fail(self):
        self.assertTrue(self.results.failures)
        self.assertFalse(self.results.errors)

    def test_contracts(self):
        # test if MetaContract and SpecificReturnsContract extracted properly
        contracts = self.conman.extract_contracts(self.spider.set_meta)
        self.assertEqual(len(contracts), 4)
        self.assertEqual(frozenset(type(x) for x in contracts),
                         frozenset([UrlContract, MetaContract, SpecificReturnsContract]))

        # test if the meta is set properly
        request = self.conman.from_method(self.spider.set_meta, self.results)
        self.assertEqual(
            request.meta, {"metakey1": "metaval1", "metakey2": "metaval2"})

    def test_returns_details(self):
        response = ResponseMock()

        # returns_item
        request = self.conman.from_method(
            self.spider.returns_detail_ok, self.results)
        request.callback(response)
        self.should_succeed()

        request = self.conman.from_method(
            self.spider.returns_detail_fail, self.results)
        request.callback(response)
        self.should_fail()

    def test_returns_category_pages(self):
        response = ResponseMock()

        request = self.conman.from_method(
            self.spider.returns_detail_category_ok, self.results)
        request.callback(response)
        self.should_succeed()

        request = self.conman.from_method(
            self.spider.returns_detail_category_fail, self.results)
        request.callback(response)
        self.should_fail()
