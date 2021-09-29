import os
from flask import Flask
from flask_moment import Moment

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:admin@localhost:5432/fyyur'

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

