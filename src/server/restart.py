import datetime
import traceback
from src.server import app, db
from src.server.auth.auth import token_required
from src.server.tables import (
    RLActionSelection,
    RLWeights
)

from flask import jsonify, make_response, request
from flask.views import MethodView
from src.server.helpers import return_fail_response

import numpy as np

def restart_server(app):
    '''
    This function restarts the server by restoring the algorithm's state to the last saved state
    from the database.
    '''
    try:
        print("Restarting server")

        # Get the hyper-parameters from the database
        with app.app_context():

            # Get the algorithm
            algorithm = app.config.get("ALGORITHM")

            # Get the most recent set of hyper-parameters
            rl_weights = db.session.query(RLWeights).order_by(RLWeights.id.desc()).first()

            # Get all the columns of the most recent set of hyper-parameters
            id = rl_weights.id
            policy_id = rl_weights.policy_id
            update_timestamp = rl_weights.update_timestamp
            posterior_mean_array = np.array(rl_weights.posterior_mean_array)
            posterior_var_array = np.array(rl_weights.posterior_var_array)
            posterior_theta_pop_mean_array = np.array(rl_weights.posterior_theta_pop_mean_array)
            posterior_theta_pop_var_array = np.array(rl_weights.posterior_theta_pop_var_array)
            noise_var = rl_weights.noise_var
            random_eff_cov_array = np.array(rl_weights.random_eff_cov_array)
            hp_update_id = rl_weights.hp_update_id
            user_list = rl_weights.user_list

            params = {
                "posterior_mean_array": posterior_mean_array,
                "posterior_var_array": posterior_var_array,
                "posterior_theta_pop_mean_array": posterior_theta_pop_mean_array,
                "posterior_theta_pop_var_array": posterior_theta_pop_var_array,
                "noise_var": noise_var,
                "random_eff_cov_array": random_eff_cov_array,
            }

            rl_action_selection = db.session.query(RLActionSelection)

            rl_actions = []

            for record in rl_action_selection:

                record_dict = {}

                record_dict["user_id"] = record.user_id
                record_dict["action"] = record.action
                record_dict["state"] = record.state_vector
                record_dict["act_prob"] = record.act_prob
                record_dict["reward"] = record.reward
                record_dict["decision_index"] = record.user_decision_idx

                rl_actions.append(record_dict)
        
        # Set the algorithm's state to the most recent set of hyper-parameters
        status = algorithm.reset_rl(params, user_list, policy_id, hp_update_id, rl_actions)

        if not status:
            app.logger.error("Failed to set rl weights when restarting server")
            return False

    except Exception as e:
        app.logger.error("Error restarting server: ", e)