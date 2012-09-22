This repository contains is a sample `Flask-Dashed <https://github.com/jeanphix/Flask-Dashed>`_ application.

You may browse this `app online <http://flask-dashed.jeanphi.fr/>`_

Installation
============

Locally
-------

You need to set a secret key and your database DSN::

    export APP_SECRET=myawesomesecret
    export DATABASE_URL=sqlite:///:memory:


Heroku
------

Application::

    heroku create --stack cedar
    heroku addons:add shared-database
    git push heroku master
    heroku config:add APP_SECRET='YOURAPPLICATIONSECRET'

Github oauth API (Optional)::

    heroku config:add GITHUB_KEY='YOURGITHUBAPPKEY'
    heroku config:add GITHUB_SECRET='YOURGITHUBSECRET'
