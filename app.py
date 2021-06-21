# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, jsonify
from werkzeug.exceptions import (
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    InternalServerError,
)
from dynaconf import settings
import elasticsearch
from index_api.routes import index_blueprint
from search_api.routes import search_blueprint
from health_check import health_check
from extensions import authorization, tenant_service
from extensions.opentelemetry import config_opentelemetry


def create_app():
    app = Flask(__name__)
    tenant_service.init_app(settings.TIS_URL)
    authorization.init_app(app)
    register_blueprint(app)
    register_error_handlers(app)
    config_opentelemetry(
        app,
        service_name=settings.SERVICE_NAME,
        agent_host=settings.OPENTELEMETRY_AGENT_HOST,
        agent_port=settings.OPENTELEMETRY_AGENT_PORT,
    )
    print("Done")
    return app


def register_blueprint(app):
    """Register Flask Blueprint"""
    app.register_blueprint(index_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(health_check)


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(elasticsearch.ElasticsearchException)
    def handle_exception(e):
        if app.debug:
            return (
                jsonify(
                    {"code": str(e), "message": "Something wrong with Elasticsearch"}
                ),
                500,
            )
        return jsonify({"code": "500", "message": "Internal Server Error"}), 500

    @app.errorhandler(BadRequest)
    def error_code_400(e):
        return jsonify({"code": "400", "message": "Bad Request"}), 400

    @app.errorhandler(Unauthorized)
    def error_code_401(e):
        return jsonify({"code": "401", "message": "Unauthorized"}), 401

    @app.errorhandler(Forbidden)
    def error_code_403(e):
        return jsonify({"code": "403", "message": "Forbidden"}), 403

    @app.errorhandler(NotFound)
    def error_code_404(e):
        return jsonify({"code": "404", "message": "Not Found"}), 404

    @app.errorhandler(InternalServerError)
    def error_code_500(e):
        return jsonify({"code": "500", "message": "Internal Server Error"}), 500


application = create_app()


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
