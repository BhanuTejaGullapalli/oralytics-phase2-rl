from src.server import app, db
from src.server.auth.auth import token_required



from src.server.tables import User,UserStatus,UserStudyPhaseEnum

from datetime import datetime

from flask import jsonify, make_response, request
from flask.views import MethodView
from src.server.helpers import return_fail_response

import traceback
def parse_date(date_str: str):
    """
    Converts a string date (YYYY-MM-DD) into a datetime.date object.
    Returns None if the format is invalid.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    
def parse_time(time_str: str):
    """
    Converts a string time like "9:30" or "09:30" into a datetime.time object.
    """
    try:
        return datetime.strptime(time_str, "%H:%M").time()  # Parse "09:30"
    except ValueError:
        return None
    
def check_all_fields_present(post_data) -> tuple[bool, str, int]:
    """
    Check if all fields are present in the post data
    """
    required_fields = ["user_id", "rl_start_date", "rl_end_date",
                       "morning_weekday", "morning_weekend",
                       "evening_weekday", "evening_weekend"]
    for field in required_fields:
        if not post_data.get(field):
            return False, f"Please provide a valid {field.replace('_', ' ')}.", 100 + required_fields.index(field)

    
    rl_start_date = parse_date(post_data.get("rl_start_date"))
    rl_end_date = parse_date(post_data.get("rl_end_date"))

    if not rl_start_date:
        return False, "Invalid rl_start_date format. Use YYYY-MM-DD.", 107
    if not rl_end_date:
        return False, "Invalid rl_end_date format. Use YYYY-MM-DD.", 108

    if(rl_end_date<=rl_start_date):
        return False, "End data can't be earlier than start date",115

    #validate time range
    morning_weekday = parse_time(post_data.get("morning_weekday"))
    morning_weekend = parse_time(post_data.get("morning_weekend"))
    evening_weekday = parse_time(post_data.get("evening_weekday"))
    evening_weekend = parse_time(post_data.get("evening_weekend"))

    if not morning_weekday or not morning_weekend:
        return False, "Invalid morning brushing time format. Use HH:MM (e.g., 09:30).", 109

    if not evening_weekday or not evening_weekend:
        return False, "Invalid evening brushing time format. Use HH:MM (e.g., 21:30).", 110

    if not (4 <= morning_weekday.hour < 16):
        return False, "Morning brushing time must be between 04:00 and 16:00.", 111
    if not (4 <= morning_weekend.hour < 16):
        return False, "Morning end brushing time must be between 04:00 and 16:00.", 112
    
    if not (16 <= evening_weekday.hour <= 23 or (0 <= evening_weekday.hour < 4)):
        return False, "Evening brushing time must be between 16:00 and 04:00.", 113

    if not (16 <= evening_weekend.hour <= 23 or (0 <= evening_weekend.hour < 4)):
        return False, "Evening brushing time must be between 16:00 and 04:00.", 114



    return True, None, None


class RegisterAPI(MethodView):
    """
    Register users (API called by the client to send info about users)
    """

    @token_required
    def post(self):

        app.logger.info("RegisterAPI called")

        # get the post data
        post_data = request.get_json()

        app.logger.info(f"post_data: {post_data}")

        # check if user already exists
        user = User.query.filter_by(user_id=post_data.get("user_id")).first()
        # if user does not exist, add the user
        # needs user_id, rl_start_date, rl_end_date in post_data
        try:
            if not user:
                # Check all fields are present
                status, message, ec = check_all_fields_present(post_data)
                if not status:
                    return return_fail_response(message, 202, ec)
                
                rl_start_date = parse_date(post_data.get("rl_start_date"))
                rl_end_date = parse_date(post_data.get("rl_end_date"))
                morning_weekday = parse_time(post_data.get("morning_weekday"))
                morning_weekend = parse_time(post_data.get("morning_weekend"))
                evening_weekday = parse_time(post_data.get("evening_weekday"))
                evening_weekend = parse_time(post_data.get("evening_weekend"))
                
                user = User(
                    user_id=str(post_data.get("user_id")),
                    rl_start_date=rl_start_date,  
                    rl_end_date=rl_end_date,
                    morning_weekday=morning_weekday,
                    morning_weekend=morning_weekend,
                    evening_weekday=evening_weekday,
                    evening_weekend=evening_weekend
                )
                user_status = UserStatus(user_id=str(post_data.get("user_id")),
                                         study_phase=UserStudyPhaseEnum.REGISTERED)



                # insert the user and userstatus
                try:
                    db.session.add(user)
                    db.session.add(user_status)
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": f"User {post_data.get('user_id')} was added!",
                    }
                    return make_response(jsonify(responseObject), 201)
                except Exception as e:
                    db.session.rollback()
                    app.logger.error("Error adding user info to internal database: %s", e)
                    app.logger.error(traceback.format_exc())
                    if app.config.get("DEBUG"):
                        print(e)
                        traceback.print_exc()
                    error_message = "Some error occurred while adding user info to internal database. Please try again."
                    ec = 111
                    return return_fail_response(error_message, 401, ec)

            else:
                message = f"User {post_data.get('user_id')} already exists."
                ec = 112
                return return_fail_response(message, 202, ec)
            
        except Exception as e:
            if app.config.get("DEBUG"):
                print(e)  # TODO: Set it to logger
            app.logger.error("Error adding user info to internal database: %s", e)
            app.logger.error(traceback.format_exc())
            db.session.rollback()
            message = "Some error occurred while adding user info to internal database. Please try again."
            ec = 113
            return return_fail_response(message, 401, ec)
