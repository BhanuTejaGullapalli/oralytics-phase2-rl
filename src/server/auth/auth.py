# src/server/auth/auth.py

# Sets up authentication token based API

from functools import wraps

import jwt
from flask import request, abort
from src.server import app
from src.server.auth.models import Client


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers.get("Authorization")
            try:
                token = token.split(" ")[1]
            except IndexError:
                app.logger.error("Bearer token malformed.")
                return {
                    "message": "Bearer token malformed.",
                    "data": None,
                    "status": "Unauthorized",
                    "error_code": 0,
                }, 401
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "status": "Unauthorized",
                "error_code": 1,
            }, 401
        try:
            print(token)
            data = Client.decode_auth_token(token)
            print(data)
            current_client = None
            # import pdb; pdb.set_trace()
            if not isinstance(data, str):
                current_client = Client.query.filter_by(id = data).first()
            if current_client is None:
                app.logger.error("Client not found. Invalid Authentication token!")
                return {
                    "message": "Invalid Authentication token!",
                    "status": "Unauthorized",
                    "error_code": 2,
                }, 401
        except Exception as e:
            app.logger.error(e)
            return {
                "message": "Something went wrong",
                "status": "Internal Server Error",
                "error_code": 3,
            }, 500

        return f(*args, **kwargs)

    return decorated