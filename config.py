import os
import sys

SECRET_KEY = os.environ['APP_SECRET']
DEBUG = False

try:
    if 'DATABASE_URL' in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
except:
    print "Unexpected error:", sys.exc_info()

GITHUB = None
if 'GITHUB_KEY' and 'GITHUB_SECRET' in os.environ:
    GITHUB = {
        'base_url': 'https://api.github.com/',
        'request_token_url': None,
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'consumer_key': os.environ['GITHUB_KEY'],
        'consumer_secret': os.environ['GITHUB_SECRET'],
    }
