# -*- coding: utf-8 -*-

# Item pipelines
import logging
import hashlib
from wsgiref.handlers import format_date_time
import time
import itertools

import psycopg2
from psycopg2.extensions import AsIs
from psycopg2.extras import Json
import requests
from scrapy import signals
from scrapy.pipelines.files import FilesPipeline
from twisted.enterprise import adbapi
from twisted.internet import threads

logger = logging.getLogger(__name__)


class DBStorePipeline(object):
    '''
    This class save the crawled item to a PostgreSQL table
    The db operation is async and managed by the twisted reactor loop.
    (References from https://gist.github.com/tzermias/6982723)
    '''

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls(crawler.stats, crawler.settings)
        crawler.signals.connect(instance.spider_closed, signals.spider_closed)
        return instance

    def __init__(self, stats, settings):
        # Instantiate DB
        self.dbpool = adbapi.ConnectionPool('psycopg2', settings['DB_DSN'])
        self.stats = stats

    def spider_closed(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        table = getattr(item, "db_table", None)
        if not table:
            return item

        query = self.dbpool.runInteraction(self._save_item, table, item)
        query.addErrback(self._handle_error)
        return item

    def _save_item(self, tx, table, item):

        skip_fields = getattr(item, "db_skip_fields", [])

        cols = [k for k in item if k not in skip_fields]
        self._insert_row(tx, table, cols, item)
        self.stats.inc_value('database/records_added')
        if hasattr(item, "db_helper_table_rows"):
            helper_table, helper_rows = item.db_helper_table_rows()
            if helper_rows:
                self._insert_row(tx, helper_table,
                                 helper_rows[0].keys(), *helper_rows)
                self.stats.inc_value(
                    'database/records_added', len(helper_rows))

        return item

    def _insert_row(self, tx, table, cols, *rows):
        val_fmt = "({})".format(",".join(itertools.repeat("%s", len(cols))))

        def mk_row_param(row):
            return tuple(row[k] for k in cols)
        data_str = ','.join(tx.mogrify(val_fmt, mk_row_param(row)).decode('utf-8')
                            for row in rows)
        q = "INSERT INTO {} ({}) VALUES ".format(table, ",".join(cols))
        tx.execute(q + data_str)

    def _handle_error(self, e):
        logger.error("failed to track item to DB: %s", e)


class UpYunStore(object):

    OPERATOR = None
    SIGNATURE = None

    HEADERS = {
        'Cache-Control': 'max-age=172800',
    }

    def __init__(self, uri):
        assert uri.startswith('upyun://')
        self.session = requests.Session()
        self.bucket, self.prefix = uri[8:].split("/", 1)

    def stat_file(self, path, info):
        """
        TODO fetch and return file meta info from cloud
        """
        return {}

    def persist_file(self, path, buf, info, meta=None, headers=None):
        """Upload file to Azure blob storage"""
        headers = {
            "Authorization": "UPYUN: {}:{}".format(self.OPERATOR, self.SIGNATURE),
            "Date": format_date_time(int(time.time())),
        }
        url = "http://v0.api.upyun.com:5000/{}/{}{}".format(
            self.bucket,  self.prefix, path)

        def upload():
            try:
                res = requests.put(url, headers=headers, data=buf)
                if res.status_code != 200:
                    logger.info(
                        "failed to upload file %s to upyun, response code: %s, text:\n%s",
                        path, res.status_code, res.text)
                else:
                    logger.debug("uploaded file %s to upyun", path)
            except Exception:
                logger.warn("upload file %s to upyun failed",
                            path, exc_info=True)
        return threads.deferToThread(upload)


class MbCrawlImagesPipeline(FilesPipeline):
    STORE_SCHEMES = dict(FilesPipeline.STORE_SCHEMES)
    STORE_SCHEMES["upyun"] = UpYunStore

    @classmethod
    def from_settings(cls, settings):
        upyunStore = cls.STORE_SCHEMES["upyun"]
        upyunStore.OPERATOR = settings["UPYUN_OPERATOR"]
        UpYunStore.SIGNATURE = settings["SIGNATURE"]
        return super().from_settings(settings)
