from flask import Response, request, render_template, send_from_directory, flash
from flask.ext.login import LoginManager, UserMixin, login_required, login_user
from dragencrypt import app, bcrypt, login_manager
from dragencrypt import db
import json

# User class
# Had troubles inheriting from db.Model when this was in a separate module...
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

# Login Manager - required user loader
@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    # POST


    # Check if user exists
    email = request.form["email"]
    user_entry = User.query.filter_by(email=email).first()
    if (user_entry):
        flash("There is already an account with this password.")
        return render_template("register.html")
        
    email = request.form["email"]
    
    # Blank email or password
    if (not email or not request.form["password"]):
        flash("Email and password cannot be blank.")
        return render_template("register.html")
    
    # Create User Object
    password = bcrypt.generate_password_hash(request.form["password"])
    user = User(email, password)
    
    # Commit User to Database
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=False)

    # Flash message and redirect when finished
    flash('You have created an account!')
    return render_template('login.html')


## TEST ROUTE
@app.route('/listusers' , methods=['GET'])
def listusers():
    users = User.query.all()
    return str(users)

#  Server routes
@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/about')
def render_about():
    return render_template("about.html")

@app.route('/login', methods=['GET','POST'])
def render_login():
    if request.method == "GET":
        return render_template("login.html")
    # POST
    email = request.form["email"]
    password = request.form["password"]

    # Blank email or password
    if (not email or not password):
        flash("Email and password cannot be blank.")
        return render_template("login.html")

    # Find User
    user_entry = User.query.filter_by(email=email).first()
    if (user_entry):
        entry_password = user_entry.password
        # Compare passwords
        if (bcrypt.check_password_hash(entry_password, password)):
            flash("You have logged in!")
            login_user(user_entry, remember=False)
            return render_template("index.html")
        else:
            flash("Incorrect login details.")
    else:
        flash("There is no account with that email address associated with it.")
    return render_template("login.html")