from datetime import datetime, timedelta
import traceback
import random
from flask import jsonify, make_response, request
from flask.views import MethodView
from src.server import app, db
from src.server.auth.auth import token_required
from src.server.tables import User, UserStatus, UserStudyPhaseEnum, Action
from src.server.helpers import return_fail_response
import numpy as np


class ActionsAPI(MethodView):
    """
    Get actions for the specified user.
    """

    @staticmethod
    def check_all_fields_present(post_data: dict) -> tuple[bool, str, int]:
        """
        Check if all required fields are present and valid in the post data.
        """
        required_fields = ["user_id", "request_timestamp", "decision_window_start", "message_click_flag", "app_click_flag"]

        for field in required_fields:
            if field not in post_data:
                return False, f"'{field}' is missing.", 100 + required_fields.index(field)

        try:
            # Convert request_timestamp and decision_window_start
            for field in ["request_timestamp", "decision_window_start"]:
                if isinstance(post_data[field], str):
                    post_data[field] = datetime.strptime(post_data[field], "%Y-%m-%dT%H:%M:%S")
                elif not isinstance(post_data[field], datetime):
                    return False, f"'{field}' must be a valid datetime string or object.", 105

            # Validate message_click_data and app_click_data (must be 0 or 1)
            if post_data["message_click_flag"] not in [0, 1]:
                return False, "'message_click_flag' must be 0 or 1.", 106
            if post_data["app_click_flag"] not in [0, 1]:
                return False, "'app_click_flag' must be 0 or 1.", 107

            # Ensure that message_click_data = 1 and app_click_data = 0 is an error
            if post_data["message_click_flag"] == 1 and post_data["app_click_flag"] == 0:
                return False, "Invalid state: message_click_flag is 1 but app_click_flag is 0.", 108
            
            decision_hour = post_data["decision_window_start"].hour
            if decision_hour not in [4, 16]:
                return False, f"Invalid decision window hour: {decision_hour}. Must be 4 AM or 4 PM.", 109


            if post_data["request_timestamp"] > post_data["decision_window_start"]:
                return False, "Request timestamp is later than decision window start.", 110

        except ValueError as e:
            return False, f"Invalid date format: {e}", 111

        return True, "All fields are valid.", 200
    
    @staticmethod
    def compute_timedelta(user,idx) -> timedelta:
        if idx < 1:
            raise ValueError("Index must be >= 1")
        hours = 4 + (idx - 1) * 12
        return datetime.combine(user.rl_start_date, datetime.min.time())+timedelta(hours=hours)


    @staticmethod
    def compute_decisionidx_number(user, decision_window_start, actions_per_day=2) -> int:

        

        user_start_date = datetime.combine(user.rl_start_date, datetime.min.time()) + timedelta(hours=4)
        print((decision_window_start),(user_start_date),"computing decision index")
        time_diff = (decision_window_start - user_start_date).total_seconds() // 3600
        if time_diff<0:
            return -1
        return int(time_diff // (24 / actions_per_day)) + 1



    @staticmethod
    def get_user_action(post_data: dict, decision_idx: int) -> tuple[bool, str, int, float, int, int, float, int]:
        """
        Generate a user action with probabilities and random decisions.
        """
        random_seed = random.randint(0, 100000)
        action_prob = random.random()
        action = 1 if action_prob > 0.5 else 0

        user = User.query.filter_by(user_id=post_data["user_id"]).first()
        if not user:
            return False, "User not found.", 203, None, None, None, None, None

        if post_data["decision_window_start"].hour == 4:
            offset = random.randint(0, max(0, 10))
            decision_time = 4 + offset
        elif post_data["decision_window_start"].hour == 16:
            offset = random.randint(0, max(0, 7))
            decision_time = 16 + offset
        else:
            return False, "Requested decision time is not 4 AM or 4 PM", 203, None, None, None, None, None

        reward = random.random()

        hours = int(decision_time)
        minutes = round((decision_time - hours) * 60)
        decision_time=f"{hours:02}:{minutes:02}"

        return True, None, None, action_prob, action, decision_time, reward, random_seed

    @token_required
    def post(self):
        post_data = request.get_json()
        user_id = post_data.get("user_id")
        app.logger.info(f"Actions API called for user {user_id}")

        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return return_fail_response(f"User {user_id} does not exist.", 202, 203)

        try:
            status, message, ec = self.check_all_fields_present(post_data)
            if not status:
                return return_fail_response(message, 202, ec)

            decision_window_start = post_data["decision_window_start"]
            decision_idx = self.compute_decisionidx_number(user, decision_window_start)

            if decision_idx==-1:
                return return_fail_response(
                    f"Requesting action for a date prior to start_date. Next action should be for {user.rl_start_date}",
                    202,
                    304
                )

            existing_action = Action.query.filter_by(user_id=user_id, decision_idx=decision_idx).first()
            # if existing_action:
            #     app.logger.error(f"Duplicate action request for user {user_id} and decision index {decision_idx}")
            #     return return_fail_response(
            #         f"Action already exists for user {user_id} at decision index {decision_idx}.",
            #         202,
            #         304
            #     )

            user_status = UserStatus.query.filter_by(user_id=user_id).first()
            if user_status.study_phase == UserStudyPhaseEnum.REGISTERED:
                user_status.study_phase = UserStudyPhaseEnum.STARTED

            # if(decision_idx!=user_status.current_decision_index+1):
            #     ttime=self.compute_timedelta(user,user_status.current_decision_index+1).strftime("%Y-%m-%d %H:%M:%S")
            #     return return_fail_response(
            #         f"Requesting action for an incorrect date. Next action should be for {ttime}",
            #         202,
            #         304
            #     )
            if(decision_idx > user_status.current_decision_index+1):
                ttime=self.compute_timedelta(user,user_status.current_decision_index+1).strftime("%Y-%m-%d %H:%M:%S")
                return return_fail_response(
                    f"Requesting action for an incorrect date. Next new action should be for {ttime}",
                    202,
                    304
                )

            user_status.current_decision_index = decision_idx


            model_params, state = np.zeros(10), np.zeros(10)
            status, message, ec, user_action_prob, user_action, user_decision_time, user_reward, random_state = self.get_user_action(
                post_data, decision_idx
            )


            db.session.add(
                Action(
                    user_id=user_id,
                    decision_idx=user_status.current_decision_index,
                    decision_time=user_decision_time,
                    action=user_action,
                    action_prob=user_action_prob,
                    random_state=random_state,
                    state=state,
                    reward=user_reward,
                    decision_timestamp=decision_window_start,
                    model_parameters=model_params,
                    request_timestamp=post_data["request_timestamp"],
                )
            )

            db.session.commit()
            return make_response(
                jsonify({
                    "status": "success",
                    "message": f"action {user_action}, decision hour {user_decision_time} for user {user_id}",
                    "action":user_action,
                    "decision_hour":user_decision_time
                }),
                201
            )
        except Exception as e:
            db.session.rollback()
            app.logger.error("Error in Actions API", exc_info=True)
            return return_fail_response("An error occurred. Please try again.", 401, 208)
