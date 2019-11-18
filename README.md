# queue_backend

## Installation
Debian or Ubuntu:

#### Get project from GitHub
```
$ git clone https://github.com/maximus1998g/queue_backend.git
```

#### Python installation
```
$ sudo apt install python3.6
```

#### Virtual environment
```
$ python3 -m venv env
```

#### Django & necessary packages installation
```
$ source env/bin/activate
(env) ~$ python3 -m pip install --upgrade pip
(env) ~$ pip install -r requirements.txt
```

#### Setup postgresql
```
$ sudo apt-get postgresql-common
$ sudo -u postgres psql
postgres=#CREATE DATABASE QUEUE_DB;
postgres=#CREATE USER ADMIN WITH PASSWORD 'PASSWORD';
postgres=#GRANT ALL PRIVILEGES ON DATABASE QUESUE_DB TO "admin";
```

#### Setup Environ
Announce your local variables to .env in the directory with settings.py
Check .env.example

## Run project
```
(env) ~/queue_backend$ python manage.py runserver
```
