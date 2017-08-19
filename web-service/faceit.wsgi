#! /anaconda/envs/py35/bin/python
# ref: https://devops.profitbricks.com/tutorials/deploy-a-flask-application-on-ubuntu-1404/
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/dsteam/repos/face-it/web-service/")

from app import app as application
application.secret_key = 'SECRET_KEY_HERE'