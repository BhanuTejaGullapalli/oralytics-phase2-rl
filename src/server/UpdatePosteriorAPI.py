import datetime
import os
import traceback
import csv

import pandas as pd
from flask import jsonify, make_response, request
from flask.views import MethodView

from src.server import db, app
from src.server.auth.auth import token_required
from src.server.tables import RLActionSelection, RLWeights, StudyData, Action
from src.server.helpers import return_fail_response


class UpdatePosteriorAPI(MethodView):
    """
    Update model weights of the RL algorithm.
    """

    @staticmethod
    def check_all_fields_present(post_data) -> tuple[bool, str, int]:
        """
        Check if all required fields are present in the post data.
        """
        request_timestamp = post_data.get("request_timestamp")
        if not isinstance(request_timestamp, (str, datetime.datetime)):
            return False, "Request timestamp must be a string or datetime object.", 400

        return True, None, None

    def export_table(self, tablename, time: datetime.datetime) -> None:
        """
        Exports the table to a CSV file in a folder inside data/backups/.
        """
        # Create filename and folder
        folder = f"./data/backups/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
        filename = f"{tablename.__tablename__}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Write table data to the file
        with open(f"{folder}/{filename}", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([c.name for c in tablename.__table__.columns])
            for row in tablename.query.all():
                writer.writerow(
                    [getattr(row, c.name) for c in tablename.__table__.columns]
                )

    def backup_all_tables(self, time: datetime.datetime) -> tuple[bool, str, str, int]:
        """
        Exports all tables to CSV files in a folder.
        :return: A tuple indicating success or failure, an error message, the backup location, and an error code.
        """
        try:
            for tablename in db.Model.registry._class_registry.values():
                if hasattr(tablename, "__tablename__"):
                    self.export_table(tablename, time)
        except Exception as e:
            app.logger.error("Error backing up tables: %s", e)
            if app.config.get("DEBUG"):
                print("Error backing up tables:", e)
            return False, f"Error backing up tables: {e}", None, 500

        backup_path = f"./data/backups/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
        return True, None, backup_path, None

    @token_required
    def post(self):
        """
        Handle POST requests to update model weights.
        """
        try:
            app.logger.info("UpdatePosteriorAPI called")
            post_data = request.get_json()

            # Check if required fields are present
            status, message, error_code = self.check_all_fields_present(post_data)
            if not status:
                app.logger.error(message)
                return return_fail_response(message=message, code=400, error_code=error_code)

            # Extract request timestamp
            request_timestamp = post_data.get("request_timestamp")
            if not request_timestamp:
                return return_fail_response("timestamp missing in request data.", 400, 401)

            # Add  logic for updating model weights or other operations here- PENDING

            response_object = {
                "status": "success",
                "message": "Successfully updated parameters/posteriors.",
            }
            return make_response(jsonify(response_object)), 201

        except Exception as e:
            app.logger.error("Error updating hyper-parameters: %s", e)
            app.logger.error(traceback.format_exc())
            if app.config.get("DEBUG"):
                print(e)
                traceback.print_exc()
            return return_fail_response("An error occurred. Please try again.", 500, 402)
