from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, Join, Identity


class TruncateOverLength:
    def __init__(self, maxlen):
        self.maxlen = maxlen

    def __call__(self, val):
        if not val:
            return val

        return val[:self.maxlen]


class ProductLoader(ItemLoader):
    default_output_processor = TakeFirst()
    name_out = Compose(TakeFirst(), TruncateOverLength(512))
    description_out = Compose(TakeFirst(), TruncateOverLength(1024))
    category_out = Compose(TakeFirst(), TruncateOverLength(128))
    file_urls_out = Identity()


class BeiBeiProductLoader(ProductLoader):
    pass


class SkuLoader(ItemLoader):
    default_output_processor = TakeFirst()
    name_out = Compose(Join(), TruncateOverLength(512))


class BeiBeiSkuLoader(SkuLoader):
    pass
