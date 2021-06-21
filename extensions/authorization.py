import base64
import json

import jwt
from werkzeug.routing import ValidationError
from flask import _app_ctx_stack, request
import extensions


class Authorization(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    @property
    def auth_infos(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            preferred_username = request.headers.get(
                "X-AUTH-REQUEST-PREFERRED-USERNAME"
            )
            api_key_header = request.headers.get("X-API-KEY")
            user_info_header = request.headers.get("X-USERINFO")

            if preferred_username:
                token = request.headers.get("AUTHORIZATION")
                decoded = jwt.decode(token.replace("Bearer ", ""), verify=False)
                if not hasattr(ctx, "auth_info"):
                    ctx.auth_info = {
                        "username": preferred_username,
                        "auth_info": decoded,
                    }
                return ctx.auth_info

            elif api_key_header:
                user_info = json.loads(base64.b64decode(api_key_header))
                user_name = user_info["username"]
                if not user_name == "system":  # Validate user
                    raise ValidationError("Unauthorized")

                if not hasattr(ctx, "auth_info"):
                    ctx.auth_info = {
                        "username": user_name,
                        "auth_info": {
                            "roles": [
                                extensions.tenant_service.get_current().get(
                                    "ROLE_ADMIN"
                                )
                            ]
                        },
                    }
                return ctx.auth_info

            elif user_info_header:
                user_info = json.loads(
                    base64.b64decode(
                        user_info_header + "=" * (-len(user_info_header) % 4)
                    )
                )
                if not hasattr(ctx, "auth_info"):
                    ctx.auth_info = {
                        "username": user_info["username"],
                        "auth_info": user_info,
                    }
                return ctx.auth_info

            else:
                raise ValidationError("Unauthorized")
