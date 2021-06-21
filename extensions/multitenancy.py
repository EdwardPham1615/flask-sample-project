from typing import Dict
import requests
from flask import request
import elasticsearch
from redlock import RedLockFactory
import redis
import logging


class InvalidTenant(Exception):
    pass


class TenantService(object):
    def __init__(self, tis_url=None):
        self.tis_url = tis_url
        self.tenants: Dict[str, Dict] = {}
        self.es: Dict[str, elasticsearch.Elasticsearch] = {}
        self.redlock_factory: Dict[str, RedLockFactory] = {}
        self.routing_map: Dict[str, str] = {}
        if tis_url is not None:
            self.init_app(tis_url)
        self.logger = logging.getLogger(__name__)

    def init_app(self, tis_url):
        self.tis_url = tis_url
        res = requests.get(tis_url + "/tenants/list.json")
        res.raise_for_status()
        list_tenants = res.json()
        self.get_tenant(list_tenants["tenants"])

    def get_tenant(self, list_tenants):
        for tenant_id in list_tenants:
            res = requests.get(self.tis_url + "/tenants/" + tenant_id + ".json")
            res.raise_for_status()
            tenant = res.json()
            self.tenants[tenant_id] = tenant
            self.routing_map[tenant["HOSTNAME"]] = tenant_id
        self.init_es()
        self.init_redlock()

    def init_es(self):
        for tenant_id, info in self.tenants.items():
            self.es[tenant_id] = elasticsearch.Elasticsearch(info["ELASTICSEARCH_HOST"])
            self.logger.info(f"Successfully initialized {tenant_id}'s elasticsearch")

    def init_redlock(self):
        for tenant_id, info in self.tenants.items():
            conn = redis.from_url(info["REDIS_CACHE_URI"])
            self.redlock_factory[tenant_id] = RedLockFactory(
                connection_details=[conn]
            )

    def get_current(self):
        tenant_id = request.headers.get("X-TENANT-ID", None)
        if tenant_id is None:
            host = request.headers.get("Host")
            tenant_id = self.routing_map.get(host)
            if host is None:
                raise InvalidTenant
        return self.tenants[tenant_id]

    def get_es(self, tenant_id):
        es = self.es.get(tenant_id)
        if es is None:
            raise InvalidTenant
        return es

    def get_redlock(self, tenant_id):
        redlock_factory = self.redlock_factory.get(tenant_id)
        if redlock_factory is None:
            raise InvalidTenant
        return redlock_factory
