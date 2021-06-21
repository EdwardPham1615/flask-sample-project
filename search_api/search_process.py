def search(query_string, from_, size, sort, tenant_config, es):
    body = {
        "size": size,
        "from": from_,
        "query": {"query_string": {"query": query_string}},
        "track_total_hits": "true"
    }

    sort_param = make_sort_param(sort)
    body.update(sort_param)

    index = f"{tenant_config.get('INDEX_PREFIX')}_*"
    data = es.search(index=index, body=body)

    _response_data = [i for i in data["hits"]["hits"]]
    return {
        "result": process_data(_response_data),
        "count": data["hits"]["total"]["value"],
    }


def make_sort_param(sort):
    """
    input: -StudyDate
    output: {
            "sort": {
                StudyDate: {
                    "order": "DESC"
                }
            }
        }
    """
    if not sort:
        return {}

    order = "DESC" if sort[0] == "-" else "ASC"
    field = sort if order == "ASC" else sort[1:]
    field_keyword_type = field + ".keyword"

    return {
        "sort": {
            field_keyword_type: {
                "order": order,
                "mode": "max",
                "unmapped_type": "keyword",
            }
        }
    }


def process_data(data):
    """
        Datas are ElasticSearch's infomation
        Need to convert it and return to client
    """
    pass
