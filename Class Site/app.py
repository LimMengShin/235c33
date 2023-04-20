from flask import Flask, render_template, request, redirect, flash
import sqlite3

def amt_is_valid(amt):
    try:
        amt = float(amt)
    except ValueError:
        return False
    else:
        return True

app = Flask(__name__)
app.secret_key = "secret key"


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
        cur.execute("DELETE FROM class_funds")
        cur.executemany("INSERT INTO class_funds (id, name, funds) VALUES (?, ?, ?)",
                        ([idx+1, name, 0] for idx, name in enumerate(NAMES)))
        con.commit()
    return redirect("/funds")


@app.route("/funds", methods=["GET", "POST"])
def funds():
    con = sqlite3.connect("class_funds.db")
    with con:
        cur = con.cursor()

        if request.method == "POST":
            group = request.form.get("group")
            amt = request.form.get("amt")

            if group not in GROUPS:
                flash('Error! Invalid group.')
            elif not amt_is_valid(amt):
                flash('Error! Invalid amount.')
            else:
                amt = float(amt)*100
                if group == "Class Add":
                    con.execute("UPDATE class_funds SET funds=funds+?", (int(amt),))
                elif group == "Class Subtract":
                    con.execute("UPDATE class_funds SET funds=funds-?", (int(amt),))

                elif group == "Individual Add":
                    student_name = request.form.get("indv")
                    if student_name not in NAMES:
                        flash('Error! Invalid student name.')
                    con.execute("UPDATE class_funds SET funds=funds+? WHERE name=?", (int(amt),student_name))

                elif group == "Individual Subtract":
                    student_name = request.form.get("indv")
                    if student_name not in NAMES:
                        flash('Error! Invalid student name.')
                    con.execute("UPDATE class_funds SET funds=funds-? WHERE name=?", (int(amt),student_name))

                else:
                    subject = d[group]
                    students = [list(id) for id in cur.execute(f"SELECT id from {subject}").fetchall()]
                    con.executemany("UPDATE class_funds SET funds=funds-? WHERE id=?", ([int(amt), id[0]] for id in students))
                
                con.commit()

        funds = cur.execute("SELECT * from class_funds").fetchall()


    return render_template("class_funds.html", funds=funds, groups=GROUPS, names=NAMES)
    
