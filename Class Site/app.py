from flask import Flask, render_template, request, redirect, flash, abort
import sqlite3
from datetime import datetime

def amt_is_valid(amt):
    try:
        amt = float(amt)
    except ValueError:
        return False
    else:
        return True

app = Flask(__name__)
app.secret_key = "secret key"
prevs = ["", 0, "", ""] # group, amt, name, date
NAMES = ['Amelia', 'Gillian', 'Louissa', 'Yong Jia', 'Isis', 'Winona', 'Maydalynn', 'Min Jia', 'Nuo Xin', 'Yi Xin', 'Justin',\
        'Toby', 'Ethan', 'Zhong Yu', 'Kingster', 'Jun Rui', 'Xiang Ling', 'Hua Yu', 'Javier', 'Meng Shin', 'Matthew', 'Cayden',\
        'Reidon', 'Yun Hao', 'Nicholas', 'Theodore', 'Xander', 'Aaron']
GROUPS = ['Class Add', 'Class Subtract', 'H2 Physics', 'H2 Mathematics', 'H2 Economics', 'H2 Computing', 'Individual Add', 'Individual Subtract']

d = {
    'H2 Physics': 'h2_physics',
    'H2 Mathematics': 'h2_math',
    'H2 Economics': 'h2_econs',
    'H2 Computing': 'h2_comp',
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reset")
def reset():
    with sqlite3.connect("class_funds.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE class_funds SET funds=0")
        con.commit()
    return redirect("/funds")


@app.route("/clear")
def clear():
    with sqlite3.connect("logs.db") as con2:
        cur2 = con2.cursor()
        cur2.execute("DELETE FROM logs")
        con2.commit()
    return redirect("/logs")


@app.route("/funds", methods=["GET", "POST"])
def funds():
    with sqlite3.connect("class_funds.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        if request.method == "POST":
            group = request.form.get("group")
            amt = request.form.get("amt")
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            num_affected = 0

            if group not in GROUPS:
                flash('Error! Invalid group.', 'alert-danger')
            elif not amt_is_valid(amt):
                flash('Error! Invalid amount.', 'alert-danger')
            else:
                valid = True
                total_before = cur.execute("SELECT SUM(funds) FROM class_funds").fetchone()["SUM(funds)"]
                amt = float(amt)*100
            
                prevs[0] = group
                prevs[1] = amt
                prevs[3] = date
                if group == "Class Add":
                    cur.execute("UPDATE class_funds SET funds=funds+?", (int(amt),))
                    num_affected = len(NAMES)

                elif group == "Class Subtract":
                    cur.execute("UPDATE class_funds SET funds=funds-?", (int(amt),))
                    num_affected = len(NAMES)

                elif group == "Individual Add":
                    student_name = request.form.get("indv")
                    prevs[2] = student_name
                    if student_name not in NAMES:
                        valid = False
                        flash('Error! Invalid student name.', 'alert-danger')
                    cur.execute("UPDATE class_funds SET funds=funds+? WHERE name=?", (int(amt),student_name))
                    num_affected = 1

                elif group == "Individual Subtract":
                    student_name = request.form.get("indv")
                    prevs[2] = student_name
                    if student_name not in NAMES:
                        valid = False
                        flash('Error! Invalid student name.', 'alert-danger')
                    cur.execute("UPDATE class_funds SET funds=funds-? WHERE name=?", (int(amt),student_name))
                    num_affected = 1

                else:
                    grp = d[group]
                    students = [di["id"] for di in cur.execute(f"SELECT id FROM {grp}").fetchall()]
                    cur.executemany("UPDATE class_funds SET funds=funds-? WHERE id=?", ([int(amt), id] for id in students))
                    num_affected = len(students)
                
                if valid:
                    total_after = cur.execute("SELECT SUM(funds) FROM class_funds").fetchone()["SUM(funds)"]

                    con.commit()

                    with sqlite3.connect("logs.db") as con2:
                        con2.row_factory = sqlite3.Row
                        cur2 = con2.cursor()
                        cur2.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (None, group, amt, num_affected*amt, total_before, total_after, num_affected, date))
                        con2.commit()
                    
                    redirect("/funds")
                    flash("Successfully updated values.", "alert-success")

        funds = cur.execute("SELECT * FROM class_funds").fetchall()

    return render_template("class_funds.html", funds=funds, groups=GROUPS, names=NAMES)


@app.route("/undo", methods=["POST", "GET"])
def undo():
    if request.method == 'GET':
        abort(404)

    group = prevs[0]
    amt = -prevs[1]
    name = prevs[2]
    date = prevs[3]

    with sqlite3.connect("class_funds.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        if group == "Class Add":
            con.execute("UPDATE class_funds SET funds=funds+?", (int(amt),))
        elif group == "Class Subtract":
            con.execute("UPDATE class_funds SET funds=funds-?", (int(amt),))

        elif group == "Individual Add":
            con.execute("UPDATE class_funds SET funds=funds+? WHERE name=?", (int(amt),name))

        elif group == "Individual Subtract":
            con.execute("UPDATE class_funds SET funds=funds-? WHERE name=?", (int(amt),name))

        else:
            subject = d[group]
            students = [di["id"] for di in cur.execute(f"SELECT id from {subject}").fetchall()]
            con.executemany("UPDATE class_funds SET funds=funds-? WHERE id=?", ([int(amt), id] for id in students))
        
        con.commit()
    # add functionality to delete logs
    # see indv logs
    # note bought
    # edit subject name list
    with sqlite3.connect("logs.db") as con2:
        con2.row_factory = sqlite3.Row
        cur2 = con2.cursor()
        cur2.execute("DELETE FROM logs WHERE date=?", (date,))
        con2.commit()
    
    return redirect("/funds")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    with sqlite3.connect("class_funds.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        students_h2_phy = [di["id"] for di in cur.execute("SELECT id from h2_physics").fetchall()]
        students_h2_math = [di["id"] for di in cur.execute("SELECT id from h2_math").fetchall()]
        students_h2_econs = [di["id"] for di in cur.execute("SELECT id from h2_econs").fetchall()]
        students_h2_comp = [di["id"] for di in cur.execute("SELECT id from h2_comp").fetchall()]
        print(students_h2_econs)

        if request.method == "POST":
            students_h2_phy = request.form.getlist('h2_physics', type=int)
            students_h2_math = request.form.getlist('h2_math', type=int)
            students_h2_econs = request.form.getlist('h2_econs', type=int)
            students_h2_comp = request.form.getlist('h2_comp', type=int)
            con.execute("DELETE FROM h2_physics")
            con.executemany("INSERT INTO h2_physics VALUES (?, ?)", ([id, NAMES[id-1]] for id in students_h2_phy))
            con.execute("DELETE FROM h2_math")
            con.executemany("INSERT INTO h2_math VALUES (?, ?)", ([id, NAMES[id-1]] for id in students_h2_math))
            con.execute("DELETE FROM h2_econs")
            con.executemany("INSERT INTO h2_econs VALUES (?, ?)", ([id, NAMES[id-1]] for id in students_h2_econs))
            con.execute("DELETE FROM h2_comp")
            con.executemany("INSERT INTO h2_comp VALUES (?, ?)", ([id, NAMES[id-1]] for id in students_h2_comp))
            con.commit()

        funds = cur.execute("SELECT * FROM class_funds").fetchall()

    return render_template("edit.html", names=NAMES, students_h2_phy=students_h2_phy, students_h2_math=students_h2_math, students_h2_econs=students_h2_econs, students_h2_comp=students_h2_comp)
    return render_template("class_funds.html", funds=funds, groups=GROUPS, names=NAMES)


@app.route("/logs", methods=["GET", "POST"])
def logs():
    with sqlite3.connect("logs.db") as con2:
        con2.row_factory = sqlite3.Row
        cur2 = con2.cursor()
        logs = cur2.execute("SELECT * from logs").fetchall()
        logs.sort(key=lambda item: item["id"], reverse=True)
    return render_template("logs.html", logs=logs)