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
$ sudo -u postgres psql
postgres=#CREATE DATABASE QUEUE_DB;
postgres=#CREATE USER ADMIN WITH PASSWORD 'PASSWORD';
postgres=#GRANT ALL PRIVILEGES ON DATABASE QUESUE_DB TO "admin";
```

## Run project
```
(env) ~/queue_backend$ python manage.py runserver
```
