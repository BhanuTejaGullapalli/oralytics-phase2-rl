# Oralytics V2 RL Service API

- ```/src/auth```: Stores the authentication scheme for the API
- ```/src/server```: Stores the server related code, which details the app routes for the API
- ```/src/algorithm```: Stores the RL algorithm

# Setup
- Install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- Install postgres. Download latest postgres from this [link](https://www.postgresql.org/download/)
- Set up conda environment using: ```conda env create -f miwaves.yml``` (If you are on Debian, make sure you have ``gcc`` installed, and ``libpq-dev`` installed)
- Make sure to activate the conda environment using ```conda activate miwaves```
- Clone this repository
- Navigate to the repo folder: ```cd miwaves_rl_service```
- Specify the postgres username and password in ```config.ini```. Also configure the backend API_URI there (it currently does not support authentication with token or user/pass, but that will be added once the backend api has been developed). The default backend URI is specified to be of a mock Postman API.
- Then create the data directories using the following commands
  - ```mkdir data```
  - ```mkdir data/dbs```
  - ```mkdir data/backups```
  - ```mkdir data/logs```
- Assuming the location of storing databases to ```data/dbs/```, give access to <postgres> user using the following command:\
```chown postgres:postgres fullpath/data/dbs```
- Then launch postgresql using the following command - ```psql "postgresql://<username>:<password>@localhost"```
- Then create tablespace in postgres using:
```CREATE TABLESPACE miwaves_db LOCATION 'fullpath/data/dbs';```
  Use ```\db+``` to view all tablespaces
- Then create database at the specified database location:\
  ```CREATE DATABASE flask_jwt_auth TABLESPACE miwaves_db;```\
  ```CREATE DATABASE flask_jwt_auth_test TABLESPACE miwaves_db;```\
 Sidenote: Use ```\l+``` to view all databases in all tablespaces. View tables using ```\dt```, and describe tables using ```\d+ <table_name>```
- Exit postgresql using ```\q```. You can later reconnect using ```psql -U <username> -d <database_name>``` if required.
- Set the FLASK_APP environment variable on terminal/bash before running. On Windows, set flask app name as - ```$env:FLASK_APP="src.server"```. On other platforms do - ```export FLASK_APP=src.server```
- Then run the following commands to set up the databases:\
```python manage.py create_db```\
```python manage.py db init```\
```python manage.py db migrate```\
```python manage.py populate_commit_id``` (this is one time unless the code has changed)
- Now finally, run the server using the following command:\
```flask run```

If commands have added users to the database, and you want to reset the database completely (erase it and start afresh), use the following set of commands in order:\
```python manage.py drop_db``` # To drop the entire database USE WITH CAUTION\
```python manage.py db stamp head``` # To reset the database after drop_db\
```python manage.py create_db``` # To create the database again\
```python manage.py db migrate``` # To migrate the database after drop_db\
```python manage.py db upgrade``` # To upgrade the database after drop_db

# Testing
There is a automated testing suite, which simulates the API calls and tests the responses. To run this suite, look under tests, the main file is ```api.py```. Use flask to run it (maybe run it on port 4000 using ```flask run --port 4000```). The tests are not yet using unittest, but will use it in the future. This file mimics backend API, and provides the ```/ema_study``` endpoint for the RL API to get data from.

# API Routes
- ```/auth/register```: Register a new client to call APIs to get action and provide data. Responds with a ```status``` message - either ```fail``` or ```success```. If ```success```, then return the ```auth_token``` which will be used in headers of subsequent RL API calls as a bearer token to authenticate the client. Currently you can only register **one** client.
- ```/auth/login```: Login an existing client to call APIs to get action and provide data. Responds with a ```status``` message - either ```fail``` or ```success```. If ```success```, then return the ```auth_token``` which will be used in headers of subsequent RL API calls as a bearer token to authenticate the client.
- ```/auth/logout```: Logout an existing client. Responds with a ```status``` message - either ```fail``` or ```success```. If ```success```, then the current ```auth_token``` for that particular user's login is blacklisted - the user has to login again to generate a new token.
