# -*- coding: utf-8 -*-
"""Function based view example """
from flask import Blueprint, request, jsonify
from search_api.search_process import search
from extensions import tenant_service

search_blueprint = Blueprint("search", __name__, url_prefix="/")


@search_blueprint.route("", methods=["GET", "POST"])
def search_api():
    tenant_config = tenant_service.get_current()
    es = tenant_service.get_es(tenant_config["TENANT_ID"])
    params = None
    if request.method == "GET":
        params = request.args
    if request.method == "POST":
        params = request.get_json()

    from_ = params.get("offset", 0)
    size = params.get("limit", 100)
    query_string = params.get("query_string", "*")
    sort = params.get("sort")

    try:
        user_roles = authorization.auth_infos.get("auth_info").get("roles", [])
    except Exception:
        raise ValidationError("Can not get user's roles")

    if tenant_config.get("ROLE_ADMIN") not in user_roles:
        query_string = (
            f"{query_string} AND (Owner:{authorization.auth_infos.get('username')})"
        )

    res = search(query_string, from_, size, sort, tenant_config, es)

    return jsonify(
        {"count": res["count"], "data": res["result"], "message": "Successful"}
    )
