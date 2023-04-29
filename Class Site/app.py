from flask import Flask, render_template, request, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import SubmitField, PasswordField, StringField, TextAreaField, SelectField, DecimalField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from datetime import datetime


prevs = ["", 0, "", ""] # group, amt, name, date
NAMES = ['Amelia', 'Gillian', 'Louissa', 'Yong Jia', 'Isis', 'Winona', 'Maydalynn', 'Min Jia', 'Nuo Xin', 'Yi Xin', 'Justin',\
        'Toby', 'Ethan', 'Zhong Yu', 'Kingster', 'Jun Rui', 'Xiang Ling', 'Hua Yu', 'Javier', 'Meng Shin', 'Matthew', 'Cayden',\
        'Reidon', 'Yun Hao', 'Nicholas', 'Theodore', 'Xander', 'Aaron']
GROUPS = ['Class Add', 'Class Subtract', 'H2 Physics', 'H2 Mathematics', 'H2 Economics', 'H2 Computing', 'Individual Add', 'Individual Subtract']


app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkeyjajaja"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///class_funds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={"autoflush": False})

indv_logs = db.Table(
    'indv_logs',
    db.Column('user_id', db.Integer, db.ForeignKey('funds.id')),
    db.Column('log_id', db.Integer, db.ForeignKey('logs.id')),
)

student_groups = db.Table(
    'student_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('funds.id')),
    db.Column('subject_name', db.String(100), db.ForeignKey('subjects.subject_name'))
)

class Funds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    funds = db.Column(db.Integer)
    groups = db.relationship('Subjects', secondary=student_groups, backref='students')
    involved_logs = db.relationship('Logs', secondary=indv_logs, backref='involved')
    def __repr__(self):
        return f'<Name {self.name}>'


class Logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grp = db.Column(db.String(100), nullable=False)
    amt = db.Column(db.Integer, nullable=False)
    total_before = db.Column(db.Integer)
    total_changed = db.Column(db.Integer)
    total_after = db.Column(db.Integer)
    num_affected = db.Column(db.Integer)
    date = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.String(100)) 

    def __repr__(self):
        return f'<Log {self.id}>'


class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Subject {self.subject_name}>'


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], render_kw={'placeholder': 'Enter username'})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={'placeholder': 'Enter Password'})
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class UpdateFundForm(FlaskForm):
    group = SelectField("Select a group", choices=[(sbj, sbj) for sbj in GROUPS], validators=[DataRequired()], render_kw={'onchange': 'getOption()'})
    indiv = SelectField("Select a student", choices=[(name, name) for name in NAMES])
    amt = DecimalField("Amount", validators=[DataRequired()], render_kw={'placeholder': 'Amount'})
    rmks = TextAreaField("Remarks", validators=[Length(min=0, max=100)], render_kw={'placeholder': 'Remarks'})
    submit = SubmitField("Update")
    

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/reset")
def reset():
    Funds.query.update({Funds.funds: 0})
    db.session.commit()
    return redirect("/funds")


@app.route("/clear")
def clear():
    Logs.query.delete()
    db.session.commit()
    return redirect("/logs")


@app.route("/funds", methods=["GET", "POST"])
def funds():
    form = UpdateFundForm()

    if form.validate_on_submit():
        group = form.group.data
        student_name = form.indiv.data
        amt = form.amt.data
        remarks = form.rmks.data
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_before = Funds.query.with_entities(func.sum(Funds.funds).label('total')).first().total
        #total_before = cur.execute("SELECT SUM(funds) FROM class_funds").fetchone()["SUM(funds)"]
        amt = int(float(amt)*100)
        
        prevs[0] = group
        prevs[1] = amt
        prevs[3] = date

        if group == "Class Add":
            num_affected = Funds.query.update({Funds.funds: Funds.funds+amt})
            student_names = NAMES

        elif group == "Class Subtract":
            num_affected = Funds.query.update({Funds.funds: Funds.funds-amt}) 
            student_names = NAMES

        elif group == "Individual Add":
            prevs[2] = student_name
            num_affected = Funds.query.where(Funds.name==student_name).update({Funds.funds: Funds.funds+amt})
            student_names = [student_name]

        elif group == "Individual Subtract":
            prevs[2] = student_name
            num_affected = Funds.query.where(Funds.name==student_name).update({Funds.funds: Funds.funds-amt})
            student_names = [student_name]

        else:
            subject = Subjects.query.where(Subjects.subject_name==group).first();
            student_names = [s.name for s in subject.students]
            num_affected = Funds.query.where(Funds.groups.contains(subject)).update({Funds.funds: Funds.funds-amt})
        

        total_after = Funds.query.with_entities(func.sum(Funds.funds).label('total')).first().total

        db.session.commit()

        new_log = Logs(
            grp = group,
            amt = amt,
            total_before = total_before,
            total_changed = total_after-total_before,
            total_after = total_after,
            num_affected = num_affected,
            date = date,
            remarks=remarks
        )
        
        #Add this update into logs
        db.session.add(new_log)
        db.session.commit()

        
        new_log.involved = []
        db.session.commit()

        #Make relational db for individual logs
        for q in Funds.query.where(Funds.name.in_(student_names)).all():
            new_log.involved.append(q)
        
        print(new_log.involved)
        
        db.session.commit()

        redirect("/funds")
        flash("Successfully updated values.", "alert-success")


    funds = Funds.query.all()

    return render_template("class_funds.html", form=form, funds=funds, groups=GROUPS, names=NAMES)


@app.route("/undo", methods=["POST", "GET"])
def undo():
    if request.method == 'GET':
        abort(404)

    group = prevs[0]
    amt = -prevs[1]
    student_name = prevs[2]
    date = prevs[3]

    if group == "Class Add":
        Funds.query.update({Funds.funds: Funds.funds+amt})

    elif group == "Class Subtract":
        Funds.query.update({Funds.funds: Funds.funds-amt}) 

    elif group == "Individual Add":
        Funds.query.where(Funds.name==student_name).update({Funds.funds: Funds.funds+amt})

    elif group == "Individual Subtract":
        Funds.query.where(Funds.name==student_name).update({Funds.funds: Funds.funds-amt})

    else:
        subject = Subjects.query.where(Subjects.subject_name==group).first();
        Funds.query.where(Funds.groups.contains(subject)).update({Funds.funds: Funds.funds-amt})


    #Delete logs for this update
    Logs.query.where(Logs.date==date).delete()
    db.session.commit()

    
    return redirect("/funds")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    
    subjects = Subjects.query.all()
    funds = Funds.query.all()
    
    if request.method == "POST":
        for sbj in subjects:
            student_list = request.form.getlist('_'.join(sbj.subject_name.split()))
            print(student_list)
            sbj.students = []
            db.session.commit()
            students = Funds.query.where(Funds.id.in_(student_list)).all()
            for student in students:
                sbj.students.append(student)

    return render_template("edit.html", names=NAMES, subjects=subjects, funds=funds)

    
@app.route("/logs", methods=["GET", "POST"])
def logs():
    logs = Logs.query.order_by(Logs.id.desc()).all()
    return render_template("logs.html", logs=logs)


@app.route("/indv-logs", methods=["GET", "POST"])
def indv_logs():
    indv_logs_list = []
    if request.method == "POST":
        name = request.form.get("indv")
        if name not in NAMES:
            flash('Error! Invalid student name.', 'alert-danger')
        else:
            student = Funds.query.where(Funds.name==name).first()
            indv_logs_list = Logs.query.where(Logs.involved.contains(student)).order_by(Logs.id.desc()).all()
            
    return render_template("indv_logs.html", names=NAMES, indv_logs_list=indv_logs_list)


@app.errorhandler(404)
def not_found(error):
    return redirect("/404")


@app.route("/404")
def fof():
    return render_template("404.html")