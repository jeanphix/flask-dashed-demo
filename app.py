# -*- coding: utf-8 -*-
import os
import wtforms

from werkzeug import OrderedMultiDict

from flask import Flask, redirect, url_for, request, flash, session
from flask_dashed.admin import Admin
from flask_dashed.ext.sqlalchemy import ModelAdminModule, model_form
from flaskext.sqlalchemy import SQLAlchemy
from flaskext import oauth
from sqlalchemy.orm import aliased, contains_eager


app = Flask(__name__)
app.config.from_pyfile(os.path.join(app.root_path, 'config.py'))
# SQLAlchemy
db = SQLAlchemy(app)
db_session = db.session


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return '<Company %r>' % self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    is_active = db.Column(db.Boolean())


class Profile(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id),
        nullable=True)

    user = db.relationship(User, backref=db.backref("profile",
        remote_side=id, uselist=False, cascade="all, delete-orphan"))

    company = db.relationship(Company, backref=db.backref("staff"))


user_group = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    users = db.relationship("User", secondary=user_group,
        backref=db.backref("groups", lazy='dynamic'))

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return '<Group %r>' % self.name


db.create_all()


UserForm = model_form(User, db_session, exclude=['password'])


class UserForm(UserForm):
    """Embeds OneToOne has FormField."""
    profile = wtforms.FormField(model_form(Profile, db_session,
        exclude=['user'], base_class=wtforms.Form))


class UserModule(ModelAdminModule):
    model = User
    db_session = db_session
    profile_alias = aliased(Profile)

    list_fields = OrderedMultiDict((
        ('id', {'label': 'id', 'column': User.id}),
        ('username', {'label': 'username', 'column': User.username}),
        ('profile.name', {'label': 'name', 'column': profile_alias.name}),
        ('profile.location', {'label': 'location',
            'column': profile_alias.location}),
    ))

    list_title = 'user list'

    searchable_fields = ['username', 'profile.name', 'profile.location']

    order_by = ('id', 'desc')

    list_query_factory = model.query\
           .outerjoin(profile_alias, 'profile')\
           .options(contains_eager('profile', alias=profile_alias))\

    form_class = UserForm

    def create_object(self):
        user = self.model()
        user.profile = Profile()
        return user


class GroupModule(ModelAdminModule):
    model = Group
    db_session = db_session
    form_class = model_form(Group, db_session, only=['name'])


class CompanyModule(ModelAdminModule):
    model = Company
    db_session = db_session
    form_class = model_form(Company, db_session, only=['name'])


admin = Admin(app, title="my business")
security = admin.register_node('/security', 'security', 'security management')
user_module = admin.register_module(UserModule, '/users', 'users',
    'users', parent=security)
group_module = admin.register_module(GroupModule, '/groups', 'groups',
    'groups', parent=security)
company_module = admin.register_module(CompanyModule, '/companies',
    'companies', 'companies')


@app.route('/')
def redirect_to_admin():
    return redirect('/admin')


@app.errorhandler(401)
def login_require(e):
    """HTTP<401>."""
    return redirect("%s?next=%s" % (url_for('login'), request.path))

# Oauth
if app.config['GITHUB']:
    oauth = oauth.OAuth()
    github = oauth.remote_app('github', **app.config['GITHUB'])

    admin.add_path_security('/', lambda: 'github_token' in session,
        http_code=401)

    @app.route('/login')
    def login():
        """Signs in via github.
        """
        return github.authorize(callback=url_for('github_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True))

    @app.route('/logout')
    def logout():
        del session['user']
        return redirect(url_for('home'))

    @github.tokengetter
    def get_github_token():
        return session.get('github_token'), ''

    @app.route('/github/callback')
    @github.authorized_handler
    def github_authorized(response):
        """Gets back user from github oauth server.
        """
        next_url = request.args.get('next') or url_for('index')
        if response is None:
            flash(u'You denied the request to sign in.')
            return redirect(next_url)
        session['github_token'] = response['access_token']
        me = github.get('/user')
        flash("you are now connected as %s" % me.data['login'], 'success')
        return redirect(next_url)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
