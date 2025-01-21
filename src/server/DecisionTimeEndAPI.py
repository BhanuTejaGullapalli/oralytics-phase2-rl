import datetime
import json
from src.server.ActionsAPI import ActionsAPI
from src.algorithm.base import RLAlgorithm
from src.server import app, db
from src.server.tables import (
    RLActionSelection,
    User,
    UserActionHistory,
    UserStatus,
    UserStudyPhaseEnum,
)
from src.server.auth.auth import token_required
from src.server.helpers import return_fail_response


from flask import jsonify, make_response, request
from flask.views import MethodView
import requests
import traceback


class DecisionTimeEndAPI(MethodView):
    """
    Upload and update brushing and engagement data in datatables
    """

    @staticmethod
    def check_all_fields_present(post_data: dict) -> tuple[bool, str, int]:
        """
        Check if all fields are present in the post data
        :param post_data: The post data from the request
        """

        if not post_data.get("user_id"):
            return False, "Please provide a valid user id.", 200
        
        if not isinstance(post_data.get("upload_timestamp", str)) or not isinstance(post_data.get("upload_timestamp", datetime.datetime)):
            return False, "Upload timestamp must be a string or datetime object.", 201
            
        if not isinstance(post_data.get("previous_upload_timestamp", str)) or not isinstance(post_data.get("previous_upload_timestamp", datetime.datetime)):
            return False, "Previous upload timestamp must be a string or datetime object.", 202
        
        if isinstance(post_data.get("upload_timestamp"), datetime.datetime) and isinstance(post_data.get("previous_upload_timestamp"), datetime.datetime):
            if post_data.get("previous_upload_timestamp") > post_data.get("upload_timestamp"):
                return False, "Previous upload timestamp cannot be greater than upload timestamp.", 203

        if not isinstance(post_data.get("data"), list):
            return False, "Data must be a list of datetime objects.", 204

        for dt in post_data.get("data"):
            if not isinstance(dt, datetime.datetime):
                return False, "All items in data must be datetime objects.", 205
            
        return True, None, None

    @token_required
    def post(self):
        app.logger.info("UploadAPI called")

        # get the post data
        post_data = request.get_json()

        # get the user_id
        user_id = post_data.get("user_id")

        app.logger.info("UploadAPI for User id: %s", user_id)

        # get the user for which decision time has ended
        user = User.query.filter_by(user_id=user_id).first()

        try:
            if not user:
                app.logger.error("User does not exist: %s", user_id)
                return return_fail_response(
                    message="User does not exist.", code=202, error_code=300
                )
            status, message, ec = self.check_all_fields_present(post_data)

            if not status:
                app.logger.error(message)
                return return_fail_response(
                    message=message,
                    code=202,
                    error_code=ec
                )
            
            data_length=len(post_data.get("data"))
            responseObject={
                "status": "success",
                "message": f"New brushing and engagement data updated for User {post_data.get('user_id')}!",
                "status": data_length,
            }
            return  make_response(jsonify(responseObject)), 201

        except Exception as e:
            app.logger.error("Some error occurred while uploading data")
            app.logger.error(traceback.format_exc())
            app.logger.error(e)
            return return_fail_response(
                message="Some error occurred while uploading. Please try again.",
                code=401,
                error_code=208
            )