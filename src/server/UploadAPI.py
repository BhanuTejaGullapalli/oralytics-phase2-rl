import datetime
import json
from src.server.ActionsAPI import ActionsAPI
from src.algorithm.base import RLAlgorithm
from src.server import app, db
from src.server.tables import (
    RLActionSelection,
    User,
    StudyData,
    Engagement,
    Action,
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

from datetime import datetime,timedelta



class UploadAPI(MethodView):
    """
    Upload and update brushing and engagement data in datatables
    """

    @staticmethod
    def check_all_fields_present(post_data: dict) -> tuple[bool, str, int]:
        """
        Check if all fields are present in the post data
        :param post_data: The post data from the request
        """
        
        # Validate user_id
        if not post_data.get("user_id"):
            return False, "Please provide a valid user id.", 200
        
        # Validate upload_timestamp
        upload_timestamp = post_data.get("upload_timestamp")
        if not isinstance(upload_timestamp, (str, datetime)):
            return False, "Upload timestamp must be a string or datetime object.", 201

        # Validate previous_upload_timestamp
        previous_upload_timestamp = post_data.get("previous_upload_timestamp")
        if not isinstance(previous_upload_timestamp, (str, datetime)):
            return False, "Previous upload timestamp must be a string or datetime object.", 202

        # Convert upload_timestamp and previous_upload_timestamp to datetime if they are strings
        if isinstance(upload_timestamp, str):
            try:
                upload_timestamp = datetime.strptime(upload_timestamp, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return False, "Invalid upload timestamp format. Must be ISO 8601.", 201

        if isinstance(previous_upload_timestamp, str):
            try:
                previous_upload_timestamp = datetime.strptime(previous_upload_timestamp, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return False, "Invalid previous upload timestamp format. Must be ISO 8601.", 202

        # Check if previous_upload_timestamp is not after upload_timestamp
        if previous_upload_timestamp > upload_timestamp:
            return False, "Previous upload timestamp cannot be greater than upload timestamp.", 203

        # Validate data
        data = post_data.get("brushing_data")

        print(data)
        if not isinstance(data, list):
            return False, "Data must be a list of items.", 204

        # Convert and validate each item in data
        converted_data = []
        seen_datetimes = set()
        for item in data:
            if not isinstance(item, list) or len(item) != 2:
                return False, "Each item in data must be a list of two elements.", 205
            
            dt, value = item
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    return False, f"Invalid datetime format in data item: {item}. Must be ISO 8601.", 206
            elif not isinstance(dt, datetime):
                return False, f"Invalid type for datetime in data item: {item}. Must be a string or datetime.", 206
            
            if not isinstance(value, int):
                return False, f"Invalid type for value in data item: {item}. Must be an integer.", 207
            
            # Check for duplicates
            if dt in seen_datetimes:
                return False, f"Duplicate datetime found in data: {dt}.", 208
            seen_datetimes.add(dt)

            converted_data.append([dt, value])
        #print(converted_data,"data")
        # Replace original data with the converted data
        post_data["brushing_data"] = converted_data
        
        return True, None, None

    @staticmethod
    def compute_decisionidx_number(user, decision_window_start, actions_per_day=2) -> int:
        user_start_date = user.rl_start_date + timedelta(hours=4)
        time_diff = (decision_window_start - user_start_date).total_seconds() // 3600
        return int(time_diff // (24 / actions_per_day)) + 1

    @token_required
    def post(self):
        app.logger.info("UploadAPI called")
        # get the post data
        post_data = request.get_json()
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
            
            
            #here bhanu
            if not status:
                app.logger.error(message)
                return return_fail_response(
                    message=message,
                    code=202,
                    error_code=ec
                )
            print(post_data["brushing_data"],"brushing_data")
            brushing_data = post_data.get("brushing_data")
            for item in brushing_data:
                dt, value = item
                print(user.rl_start_date,dt,user.rl_end_date)
                if dt < user.rl_start_date or dt > user.rl_end_date:
                    app.logger.error("Brushing Datetime not within user's study phase.")
                    return return_fail_response(
                        message="BrushingDatetime not within user's study phase.",
                        code=202,
                        error_code=301
                    )
                if value < 0 :
                    app.logger.error("Invalid brushing value.")
                    return return_fail_response(
                        message="Invalid brushing value.",
                        code=202,
                        error_code=302
                    )
                decision_idx=self.compute_decisionidx_number(user, dt)
                print(f"decision_idx:{decision_idx}")
                app.logger.info("Brushing time at %s is for decision index: %s", dt.isoformat(), decision_idx)
                user_action = Action.query.filter_by(user_id=user_id,decision_idx=decision_idx).first()
                
                if not user_action:
                    app.logger.error(
                        "No user action found for user_id: %s and decision_idx: %s",
                        user_id,
                        decision_idx
                    )
                    return return_fail_response(
                        message="No user action found for the given decision index.",
                        code=202,
                        error_code=303
                    )

                # Log and print the found user action
                app.logger.info("Found user action: %s", user_action)
                print(user_action)
                user_reward_entry = StudyData(
                    user_id=str(post_data.get("user_id")),
                    decision_idx=decision_idx,
                    action=user_action.action,
                    action_prob=user_action.action_prob,
                    decision_time=user_action.decision_time,
                    state=user_action.state,
                    raw_context=None,
                    outcome=value,
                    reward=user_action.reward,
                    request_timestamp=post_data.get("upload_timestamp"),

                )
                db.session.add(user_reward_entry)
            db.session.commit()
            app.logger.info("Brushing and engagement data updated successfully for user %s", user_id)
            responseObject = {
                "status": "success",
                "message": f"New brushing and engagement data updated for User {post_data.get('user_id')}!",
                "status": f"Processed total entries {len(post_data['brushing_data'])}",
            }

            return  make_response(jsonify(responseObject)), 201

        except Exception as e:
            print(e,"error")
            app.logger.error("Some error occurred while uploading data")
            app.logger.error(traceback.format_exc())
            app.logger.error(e)
            return return_fail_response(
                message="Some error occurred while uploading. Please try again.",
                code=401,
                error_code=208
            )