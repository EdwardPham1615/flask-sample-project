# -*- coding: utf-8 -*-
"""Function based view example """
from flask import Blueprint, Response


health_check = Blueprint("health_check", __name__, url_prefix="/health_check")


@health_check.route("/", methods=["GET"])
def health_check_api():
    return Response("OK", status=200)
