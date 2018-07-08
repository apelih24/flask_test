from flask import (Flask, Response,
                   redirect, url_for,
                   request, abort,
                   url_for, render_template,
                   flash)

from flask_login import (LoginManager, UserMixin,
                         login_required, login_user,
                         logout_user, current_user)

from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm

from flask_sqlalchemy import SQLAlchemy

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

app = Flask(__name__)
Bootstrap(app)

app.config.update(
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:Casper120197@localhost:3306/FlaskDB',
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

db = SQLAlchemy(app)


# Creating user model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(81))

    def __repr__(self):
        return '%s' % self.username


# Create table in database
# db.create_all()

# Create some users
# some_users = [User('user' + str(id), 'user' + str(id)) for id in range(1, 20)]
# Add them to the table
# for i in some_users:
#     db.session.add(i)
# Commit changes
# db.session.commit()


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=3, max=80)])


class UsersForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=3, max=80)])
    create = SubmitField(label='Create')
    delete = SubmitField(label='Delete')


# User model for FLASK-LOGIN
login_manager = LoginManager()

# flask_login
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/users', methods=['GET', 'POST'])
@login_required
def home():
    form = UsersForm()

    # POST
    if form.validate_on_submit():
        # Create button pressed
        if form.create.data:
            user = User.query.filter_by(username=form.username.data).first()
            if not user:
                user = User(username=form.username.data, password=form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('You created ' + str(user))
                return render_template('users.html', form=form, name=current_user.username, users=User.query.all())
            else:
                flash('This user is already exist')
        # Delete button pressed
        elif form.delete.data:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if form.password.data == user.password:
                    db.session.delete(user)
                    db.session.commit()
                    flash('You deleted ' + str(user))
                    return render_template('users.html', form=form, name=current_user.username, users=User.query.all())
                else:
                    flash('Password does\'t match')
            else:
                flash('No user with such username')
    # GET
    return render_template('users.html', form=form, name=current_user.username, users=User.query.all())


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # POST
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                next_page = request.args.get('next')
                # print(user_to_log.is_authenticated)
                return redirect(next_page or url_for('home'))
            else:
                return '<h1>Incorrect password</h1>'
        else:
            return abort(401)
    # GET
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(401)
def bad_authorization(e):
    return Response('<p>Login failed</p>')


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


if __name__ == '__main__':
    app.run()
