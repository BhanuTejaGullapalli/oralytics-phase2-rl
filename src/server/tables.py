# src/server/tables.py

# Server code that has the database table schemas for the users and algorithms in the trial

import datetime
import enum

from src.server import app, db
from sqlalchemy.dialects.postgresql import ARRAY


class User(db.Model):
    """User Model for storing user related details"""

    __tablename__ = "users"

    user_id = db.Column(db.String, primary_key=True, nullable=False)
    rl_start_date = db.Column(db.DateTime, nullable=True)
    rl_end_date = db.Column(db.DateTime, nullable=True)
    morning_start_hour = db.Column(db.Integer, nullable=False, default=6)
    morning_ending_hour = db.Column(db.Integer, nullable=False, default=11)
    evening_start_hour = db.Column(db.Integer, nullable=False, default=18)
    evening_ending_hour = db.Column(db.Integer, nullable=False, default=23) 

    
    # TODO: Add columns for other baseline details of the user

    def __init__(
        self,
        user_id: str,
        rl_start_date: datetime.date,
        rl_end_date: datetime.date,
        morning_start_hour:int,
        morning_ending_hour:int,
        evening_start_hour:int,
        evening_ending_hour:int
    ):
        self.user_id = user_id
        self.rl_start_date = rl_start_date
        self.rl_end_date = rl_end_date
        self.morning_start_hour = morning_start_hour
        self.morning_ending_hour = morning_ending_hour
        self.evening_start_hour = evening_start_hour
        self.evening_ending_hour=evening_ending_hour




class UserStudyPhaseEnum(enum.Enum):
    """Indicates the user's study phase as an enum"""

    REGISTERED = 1
    STARTED = 2
    ENDED = 3


class UserStatus(db.Model):
    """User Status Model for storing user status related details"""

    __tablename__ = "user_status"

    user_id = db.Column(
        db.String, db.ForeignKey("users.user_id"), primary_key=True, nullable=False
    )
    study_phase = db.Column(db.Enum(UserStudyPhaseEnum), nullable=False)
    current_decision_index = db.Column(db.Integer, nullable=False, default=0)


    def __init__(
        self,
        user_id: str,
        study_phase: UserStudyPhaseEnum,
        current_decision_index: int = 0,

    ):
        self.user_id = user_id
        self.study_phase = study_phase
        self.current_decision_index=current_decision_index



class Action(db.Model):
    """User Status Model for storing user status related details"""

    __tablename__ = "actions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, nullable=False)
    decision_idx = db.Column(db.Integer, nullable=True)
    decision_time = db.Column(db.Integer, nullable=True)
    action = db.Column(db.Integer, nullable=False, default=0)
    action_prob = db.Column(db.Float, nullable=False, default=0.5)
    random_state = db.Column(db.Integer, nullable=True)
    state = db.Column(ARRAY(db.Float), nullable=True)
<<<<<<< HEAD
    reward=db.Column(db.Float, nullable=False, default=0.0)
=======
<<<<<<< HEAD
    reward=db.Column(db.Float, nullable=False, default=0.0)
=======
>>>>>>> eec322160e066094b03a361f6664365262392458
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded
    decision_timestamp= db.Column(db.DateTime, nullable=True)
    model_parameters= db.Column(ARRAY(db.Float), nullable=True)
    request_timestamp= db.Column(db.DateTime, nullable=True)


    def __init__(
        self,
        user_id: str,
        decision_idx: int,
        decision_time: int,
        action: int,
        action_prob: float,
        random_state:int,
        state: list,
<<<<<<< HEAD
        reward: float,
=======
<<<<<<< HEAD
        reward: float,
=======
>>>>>>> eec322160e066094b03a361f6664365262392458
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded
        decision_timestamp: datetime.datetime,
        model_parameters: list,
        request_timestamp: datetime.datetime,
    ):
        self.user_id = user_id
        self.decision_idx = decision_idx
        self.decision_time = decision_time
        self.action = action
        self.action_prob = action_prob
        self.random_state=random_state
        self.state = state
<<<<<<< HEAD
        self.reward = reward
=======
<<<<<<< HEAD
        self.reward = reward
=======
>>>>>>> eec322160e066094b03a361f6664365262392458
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded
        self.decision_timestamp = decision_timestamp
        self.model_parameters = model_parameters
        self.request_timestamp = request_timestamp

<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded
    def __repr__(self):
        return (
            f"<Action user_id={self.user_id}, decision_idx={self.decision_idx}, "
            f"decision_time={self.decision_time}, action={self.action}, "
            f"action_prob={self.action_prob}>"
        )

<<<<<<< HEAD
=======
=======
>>>>>>> eec322160e066094b03a361f6664365262392458
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded

class Engagement(db.Model):
    """User Model for storing user engagments"""

    __tablename__ = "engagements"

    # user_id = db.Column(
    #     db.String, db.ForeignKey("users.user_id"), primary_key=True, nullable=False
    # )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, nullable=False)
    engagement_time = db.Column(db.DateTime, nullable=True)
    upload_time= db.Column(db.DateTime, nullable=True) 

    def __init__(
        self,
        user_id: str,
        engagement_time: datetime.datetime,
        upload_time: datetime.datetime,
    ):
        self.user_id = user_id
        self.engagement_time = engagement_time
        self.upload_time = upload_time


<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded
class StudyData(db.Model):
    """
    Database table to store study data.
    """

    __tablename__ = "study_data"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(255), nullable=False)
    decision_idx = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, nullable=False)
    action_prob = db.Column(db.Float, nullable=False)
    decision_time = db.Column(db.Integer, nullable=False)
    state = db.Column(db.ARRAY(db.Float), nullable=False)
    raw_context = db.Column(db.JSON, nullable=False)
    outcome = db.Column(db.JSON, nullable=False)
    reward = db.Column(db.Float, nullable=True)
    request_timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        user_id: str,
        decision_idx: int,
        action: int,
        action_prob: float,
        decision_time: int,
        state: list,
        raw_context: dict,
        outcome: dict,
        reward: float,
        request_timestamp: datetime.datetime,
        created_at: datetime.datetime = datetime.datetime.now().isoformat(),
    ):
        """
        Initialize the StudyData object.
        """
        self.user_id = user_id
        self.decision_idx = decision_idx
        self.action = action
        self.action_prob = action_prob
        self.decision_time = decision_time
        self.state = state
        self.raw_context = raw_context
        self.outcome = outcome
        self.reward = reward
        self.request_timestamp = request_timestamp
        self.created_at = created_at

<<<<<<< HEAD
=======
=======
>>>>>>> eec322160e066094b03a361f6664365262392458
>>>>>>> dcfa7f93f1763432f41c2691a4589cdd02c7bded








class AlgorithmStatus(db.Model):
    """Algorithm status Model for storing algorithm status related details"""

    __tablename__ = "algorithm_status"

    policy_id = db.Column(db.Integer, primary_key=True, nullable=False)
    update_time = db.Column(db.DateTime(timezone=True), nullable=False)
    update_day_in_study = db.Column(db.Integer, nullable=False)
    current_decision_time = db.Column(db.Integer, nullable=False)
    current_day_in_study = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        policy_id: int,
        update_time: datetime.datetime,
        update_day_in_study: int,
        current_decision_time: int,
        current_day_in_study: int,
    ):
        self.policy_id = policy_id
        self.update_time = update_time
        self.update_day_in_study = update_day_in_study
        self.current_decision_time = current_decision_time
        self.current_day_in_study = current_day_in_study

class RLHyperParamUpdateRequest(db.Model):
    """
    Table to store all the relevant information wrt all the hyperparameter
    update requests
    """

    __tablename__ = "rl_hyperparam_update_request"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    backup_location = db.Column(db.String, nullable=False)
    request_timestamp = db.Column(db.DateTime, nullable=False)
    request_status = db.Column(db.String, nullable=False)
    request_message = db.Column(db.String, nullable=True)
    request_error_code = db.Column(db.Integer, nullable=True)
    completed_timestamp = db.Column(db.DateTime, nullable=True)

    def __init__(
        self,
        backup_location: str,
        request_timestamp: datetime.datetime,
        request_status: str,
        request_message: str = None,
        request_error_code: int = None,
        completed_timestamp: datetime.datetime = None,
    ):
        self.backup_location = backup_location
        self.request_timestamp = request_timestamp
        self.request_status = request_status
        self.request_message = request_message
        self.request_error_code = request_error_code
        self.completed_timestamp = completed_timestamp


class RLWeights(db.Model):
    """Table to store the RL weights. Also stores a link
    to the pickle file which contains the data used to update
    to this algorithm"""

    __tablename__ = "rl_weights"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    policy_id = db.Column(db.Integer, nullable=False)
    update_timestamp = db.Column(db.DateTime, nullable=False)
    posterior_mean_array = db.Column(ARRAY(db.Float), nullable=True)
    posterior_var_array = db.Column(ARRAY(db.Float), nullable=True)
    posterior_theta_pop_mean_array = db.Column(ARRAY(db.Float), nullable=True)
    posterior_theta_pop_var_array = db.Column(ARRAY(db.Float), nullable=True)
    noise_var = db.Column(db.Float, nullable=True)
    random_eff_cov_array = db.Column(ARRAY(db.Float), nullable=True)
    code_commit_id = db.Column(
        db.String, nullable=False, default=app.config.get("CODE_VERSION")
    )
    data_pickle_file_path = db.Column(db.String, nullable=False)
    user_list = db.Column(ARRAY(db.String), nullable=True)
    hp_update_id = db.Column(db.Integer, nullable=True)

    def __init__(
        self,
        policy_id: int,
        update_timestamp: datetime.datetime,
        posterior_mean_array: list,
        posterior_var_array: list,
        posterior_theta_pop_mean_array: list,
        posterior_theta_pop_var_array: list,
        noise_var: float,
        random_eff_cov_array: list,
        hp_update_id: int,
        code_commit_id: str = app.config.get("CODE_VERSION"),
        data_pickle_file_path: str = None,
        user_list: list = None,
    ):
        self.policy_id = policy_id
        self.update_timestamp = update_timestamp
        self.posterior_mean_array = posterior_mean_array
        self.posterior_var_array = posterior_var_array
        self.posterior_theta_pop_mean_array = posterior_theta_pop_mean_array
        self.posterior_theta_pop_var_array = posterior_theta_pop_var_array
        self.noise_var = noise_var
        self.random_eff_cov_array = random_eff_cov_array
        self.code_commit_id = code_commit_id
        self.data_pickle_file_path = data_pickle_file_path
        self.user_list = user_list
        self.hp_update_id = hp_update_id

class RLActionSelection(db.Model):
    """
    Stores the user data tuple corresponding to the
    action that was executed and the components of the
    reward for that user decision time (imputed afterwards)
    """

    __tablename__ = "rl_action_selection"

    user_id = db.Column(
        db.String, db.ForeignKey("users.user_id"), primary_key=True, nullable=False
    )
    user_decision_idx = db.Column(db.Integer, primary_key=True, nullable=False)
    morning_notification_time = db.Column(ARRAY(db.Integer), nullable=False)
    evening_notification_time = db.Column(ARRAY(db.Integer), nullable=False)
    day_in_study = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, nullable=False)
    policy_id = db.Column(db.Integer, nullable=False)
    seed = db.Column(db.Integer, nullable=False)
    # policy_creation_time = db.Column(db.DateTime, nullable=False)
    prior_ema_completion_time = db.Column(db.String, nullable=True)
    action_selection_timestamp = db.Column(db.DateTime, nullable=True)
    messasge_sent_notification_timestamp = db.Column(db.String, nullable=True)
    message_click_notification_timestamp = db.Column(db.String, nullable=True)
    act_prob = db.Column(db.Float, nullable=True)
    cannabis_use = db.Column(ARRAY(db.Float), nullable=True)
    state_vector = db.Column(
        ARRAY(db.Float), nullable=True
    )  # TODO: Describe the order here
    # reward_component_vector = db.Column(ARRAY(db.Float), nullable=True)
    reward = db.Column(db.Float, nullable=True)
    row_complete = db.Column(db.Boolean, nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey("user_action_history.index"), nullable=False)

    def __init__(
        self,
        user_id: str,
        user_decision_idx: int,
        morning_notification_time: list,
        evening_notification_time: list,
        day_in_study: int,
        action: int,
        policy_id: int,
        seed: int,
        rid: int,
        # policy_creation_time: datetime.datetime,
        prior_ema_completion_time: str = None,
        message_sent_notification_timestamp: str = None,
        action_selection_timestamp: datetime.datetime = None,
        message_click_notification_timestamp: str = None,
        act_prob: float = None,
        cannabis_use: list = None,
        state_vector: list = None,
        # reward_component_vector: list = None,
        reward: float = None,
        row_complete: bool = False,
    ):
        self.user_id = user_id
        self.user_decision_idx = user_decision_idx
        self.morning_notification_time = morning_notification_time
        self.evening_notification_time = evening_notification_time
        self.day_in_study = day_in_study
        self.action = action
        self.policy_id = policy_id
        self.seed = seed
        self.rid = rid
        # self.policy_creation_time = policy_creation_time
        self.prior_ema_completion_time = prior_ema_completion_time
        self.action_selection_timestamp = action_selection_timestamp
        self.message_sent_notification_timestamp = message_sent_notification_timestamp
        self.message_click_notification_timestamp = message_click_notification_timestamp
        self.act_prob = act_prob
        self.cannabis_use = cannabis_use
        self.state_vector = state_vector
        # self.reward_component_vector = reward_component_vector
        self.reward = reward
        self.row_complete = row_complete


class UserActionHistory(db.Model):
    """
    Stores all the action calls made to the server for any given user
    along with the raw data that was sent
    """

    __tablename__ = "user_action_history"

    index = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey("users.user_id"), nullable=False)
    decision_idx = db.Column(db.Integer, nullable=False)
    finished_ema = db.Column(db.Boolean, nullable=False)
    activity_question_response = db.Column(db.String, nullable=True)
    app_use_flag = db.Column(db.Boolean, nullable=False)
    cannabis_use = db.Column(ARRAY(db.Float), nullable=True)
    reward = db.Column(db.Float, nullable=False)
    state = db.Column(ARRAY(db.Integer), nullable=False)
    action = db.Column(db.Integer, nullable=False)
    seed = db.Column(db.Integer, nullable=False)
    act_prob = db.Column(db.Float, nullable=False)
    policy_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(
        self,
        user_id: str,
        decision_idx: int,
        finished_ema: bool,
        activity_question_response: str,
        app_use_flag: bool,
        cannabis_use: list,
        reward: float,
        state: list,
        action: int,
        seed: int,
        act_prob: float,
        policy_id: int,
        timestamp: datetime.datetime,
    ):
        self.user_id = user_id
        self.decision_idx = decision_idx
        self.finished_ema = finished_ema
        self.activity_question_response = activity_question_response
        self.app_use_flag = app_use_flag
        self.cannabis_use = cannabis_use
        self.reward = reward
        self.state = state
        self.action = action
        self.seed = seed
        self.act_prob = act_prob
        self.policy_id = policy_id
        self.timestamp = timestamp
