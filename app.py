from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ctf.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# --------------------
# DATABASE MODELS
# --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    flag = db.Column(db.String(200))
    points = db.Column(db.Integer)
    level = db.Column(db.Integer)


class Solve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    challenge_id = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------
# LOGIN
# --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# --------------------
# DASHBOARD
# --------------------

@app.route("/")
@login_required
def dashboard():
    challenges = Challenge.query.filter(
        Challenge.level <= current_user.level
    ).all()
    return render_template("dashboard.html", challenges=challenges)


# --------------------
# CHALLENGE VIEW
# --------------------

@app.route("/challenge/<int:id>", methods=["GET", "POST"])
@login_required
def challenge(id):
    challenge = Challenge.query.get_or_404(id)

    if request.method == "POST":
        submitted_flag = request.form.get("flag")

        if submitted_flag == challenge.flag:

            already_solved = Solve.query.filter_by(
                user_id=current_user.id,
                challenge_id=id
            ).first()

            if not already_solved:
                current_user.score += challenge.points
                current_user.level += 1

                solve = Solve(
                    user_id=current_user.id,
                    challenge_id=id
                )

                db.session.add(solve)
                db.session.commit()

            return "Correct! 🎉"

        return "Wrong flag ❌"

    return render_template("challenge.html", challenge=challenge)


# --------------------
# SCOREBOARD
# --------------------

@app.route("/scoreboard")
@login_required
def scoreboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template("scoreboard.html", users=users)


# --------------------
# ONE TIME SETUP
# --------------------

@app.route("/setup")
def setup():
    db.create_all()

    # Create fixed users
    user1 = User(username="Ishika",
                 password=generate_password_hash("ishika@13"))
    user2 = User(username="Shreyash",
                 password=generate_password_hash("shreyash@30"))

    db.session.add(user1)
    db.session.add(user2)

    # Add 9 challenges (example first one)
    challenges = [

    Challenge(
    title="Boot Sequence Recovery",
    description="Find next number: 3,8,15,24,35,?",
    flag="48",
    points=50,
    level=1
    ),

    Challenge(
    title="Memory Parser",
    description="Reverse string and remove vowels from 'Artificial'",
    flag="ltrfcrA",
    points=75,
    level=2
    ),

    Challenge(
    title="Signal Decoder",
    description="Decode: QVVSQXtzaWduYWxfZGVjb2RlZH0=",
    flag="AURA{signal_decoded}",
    points=100,
    level=3
    ),

    Challenge(
    title="Logic Engine",
    description="5 machines make 5 chips in 5 minutes. How long for 100 machines?",
    flag="5",
    points=100,
    level=4
    ),

    Challenge(
    title="Pattern Analyzer",
    description="Triangle Square Triangle Square Triangle ?",
    flag="square",
    points=125,
    level=5
    ),

    Challenge(
    title="Hidden Console",
    description="Inspect the HTML source for the flag.",
    flag="AURA{hidden_console}",
    points=150,
    level=6
    ),

    Challenge(
    title="Encryption Node",
    description="DXUD{hqfubswlrq_rqolqh}",
    flag="AURA{encryption_online}",
    points=175,
    level=7
    ),

    Challenge(
    title="System Patch",
    description="Fix code: return a-b → ?",
    flag="return a+b",
    points=200,
    level=8
    ),

    Challenge(
    title="Core Vault",
    description="Final system unlock key",
    flag="AURA{core_unlocked}",
    points=300,
    level=9
    )

    ]

    db.session.bulk_save_objects(challenges)
    db.session.commit()

    return "Setup complete!"


if __name__ == "__main__":
    app.run(debug=True)