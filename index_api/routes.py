# -*- coding: utf-8 -*-
"""Function based view example """
from flask import Blueprint, Response, request

from extensions import tenant_service
from index_api.index_process import index

index_blueprint = Blueprint("index", __name__, url_prefix="/index")


@index_blueprint.route("", methods=["POST"])
def index_api():
    tenant_config = tenant_service.get_current()
    es = tenant_service.get_es(tenant_config["TENANT_ID"])
    redlock_factory = tenant_service.get_redlock(tenant_config["TENANT_ID"])
    body_params = request.get_json()
    index(body_params, tenant_config, es, redlock_factory)
    return Response("Index Successful", status=200)