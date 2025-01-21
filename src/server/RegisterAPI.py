from src.server import app, db
from src.server.auth.auth import token_required

from src.server.tables import User,UserStatus,UserStudyPhaseEnum,StudyData

from src.server.tables import User,UserStatus,UserStudyPhaseEnum,StudyData

from src.server.tables import User,UserStatus,UserStudyPhaseEnum



from flask import jsonify, make_response, request
from flask.views import MethodView
from src.server.helpers import return_fail_response

import traceback


def check_all_fields_present(post_data) -> tuple[bool, str, int]:
    """
    Check if all fields are present in the post data
    """

    if not post_data.get("user_id") and not isinstance(post_data.get("user_id"), str):
        return False, "Please provide a valid user id.", 100
    if not post_data.get("rl_start_date"):
        return False, "Please provide a valid rl start date.", 101
    if not post_data.get("rl_end_date"):
        return False, "Please provide a valid rl end date.", 102
    
    if not post_data.get("morning_start_hour"):
        return False, "Please provide a valid Morning start hour.", 103
    
    if not post_data.get("morning_end_hour"):
        return False, "Please provide a valid Morning end hour.", 104
    
    if not post_data.get("evening_start_hour"):
        return False, "Please provide a valid evening end hour.", 105
    
    if not post_data.get("evening_end_hour"):
        return False, "Please provide a valid evening end hour.", 106
    
    #validate time range
    morning_start_hour=post_data.get("morning_start_hour")
    morning_end_hour=post_data.get("morning_end_hour")
    evening_start_hour=post_data.get("evening_start_hour")
    evening_end_hour=post_data.get("evening_end_hour")
    # Validate morning time range [4-16]
    if not (4 <= morning_start_hour <= 16):
        return False, "Morning start hour must be between 4 and 16.", 107
    if not (4 <= morning_end_hour <= 16):
        return False, "Morning end hour must be between 4 and 16.", 108

    # Validate evening time range [16-4]
    if not (16 <= evening_start_hour <= 24 or 0 <= evening_start_hour <= 4):
        return False, "Evening start hour must be between 16 and 4.", 109
    if not (16 <= evening_end_hour <= 24 or 0 <= evening_end_hour <= 4):
        return False, "Evening end hour must be between 16 and 4.", 110
    

    if(morning_start_hour>=morning_end_hour):
        return False, "Morning start hour must be less than Morning end hour.", 111
    if(evening_start_hour>=evening_end_hour):
        return False, "Evening start hour must be less than Evening end hour.", 112

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


                
                user = User(
                    user_id=str(post_data.get("user_id")),
                    rl_start_date=post_data.get(
                        "rl_start_date"
                    ),  
                    rl_end_date=post_data.get("rl_end_date"),
                    morning_start_hour=post_data.get("morning_start_hour"),
                    morning_ending_hour=post_data.get("morning_ending_hour"),
                    evening_start_hour=post_data.get("evening_start_hour"),
                    evening_ending_hour=post_data.get("evening_ending_hour")
                )
                user_status = UserStatus(user_id=str(post_data.get("user_id")),
                                         study_phase=UserStudyPhaseEnum.REGISTERED)



                # insert the user and userstatus
                try:
                    db.session.add(user)
                    db.session.add(user_status)
                except Exception as e:
                    db.session.rollback()
                    app.logger.error("Error adding user info to internal database: %s", e)
                    app.logger.error(traceback.format_exc())
                    if app.config.get("DEBUG"):
                        print(e)
                        traceback.print_exc()
                    error_message = "Some error occurred while adding user info to internal database. Please try again."
                    ec = 111
                    return return_fail_response(error_message, 401, None)
                else:
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": f"User {post_data.get('user_id')} was added!",
                    }
                    return make_response(jsonify(responseObject)), 201, None
            else:
                message = f"User {post_data.get('user_id')} already exists."
                ec = 112
                return return_fail_response(message, 202, None)
            
        except Exception as e:
            if app.config.get("DEBUG"):
                print(e)  # TODO: Set it to logger
            app.logger.error("Error adding user info to internal database: %s", e)
            app.logger.error(traceback.format_exc())
            db.session.rollback()
            message = "Some error occurred while adding user info to internal database. Please try again."
            ec = 113
            return return_fail_response(message, 401, None)
