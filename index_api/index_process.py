import logging
from datetime import date

logger = logging.getLogger(__name__)


def get_unique_list(data):
    if isinstance(data, (list, tuple, set)):
        return list(set(data))
    return [data]


def index(body_params, tenant_config, es, redlock_factory):
    with redlock_factory.create_lock(
            " ", retry_times=10000, retry_delay=200
    ):
        exist_data = get_exist_data(" ", es, tenant_config)
        if exist_data:
            body = {}
            es.update(index=exist_data["_index"], id=exist_data["_id"], body=body, refresh=True)
        else:
            today = date.today().strftime("%Y%m")
            index = f"{tenant_config.get('INDEX_PREFIX')}_{today}"
            es.index(index=index, body=body_params, refresh=True)


def get_exist_study(id, es, tenant_config):
    """
        Check exist study or intance
    """
    query_string = f"ID:{id}"

    body = {
        "size": 1,
        "query": {"query_string": {"query": query_string}},
    }

    index = f"{tenant_config.get('INDEX_PREFIX')}_*"
    data = es.search(index=index, body=body)
    if data["hits"]["total"]["value"] > 0:
        return data["hits"]["hits"][0]
