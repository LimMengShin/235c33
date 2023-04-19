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


NAMES = ['Amelia', 'Gillian', 'Louissa', 'Yong Jia', 'Isis', 'Winona', 'Maydalynn', 'Min Jia', 'Nuo Xin', 'Yi Xin', 'Justin', 'Toby', 'Ethan', 'Zhong Yu', 'Kingster', 'Jun Rui', 'Xiang Ling', 'Hua Yu', 'Javier', 'Meng Shin', 'Matthew', 'Cayden', 'Reidon', 'Yun Hao', 'Nicholas', 'Theodore', 'Xander', 'Aaron']
GROUPS = ['Class Add', 'Class Subtract', 'H2 Physics', 'H2 Mathematics', 'H2 Economics', 'H2 Computing']
d = {
    'H2 Physics': 'h2_physics',
    'H2 Mathematics': 'h2_math',
    'H2 Economics': 'h2_econs',
    'H2 Computing': 'h2_comp',
}
funds = []


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/reset", methods=["GET", "POST"])
def reset():
    with sqlite3.connect("class_funds.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM class_funds")
        for idx, name in enumerate(NAMES):
            cur.execute("INSERT INTO class_funds (id, name, funds) VALUES (?, ?, ?)", (idx+1, name, 0))
        con.commit()
    return redirect("/funds")


@app.route("/funds", methods=["GET", "POST"])
def funds():
    with sqlite3.connect("class_funds.db") as con:
        cur = con.cursor()
        funds = [list(fund) for fund in cur.execute("SELECT * from class_funds").fetchall()]

        if request.method == "POST":
            group = request.form.get("group")
            amt = request.form.get("amt")
            if not group or group not in GROUPS or not amt or not amt_is_valid(amt):
                flash('Error! Try again.')
            else:
                amt = float(amt)*100
                if group == "Class Add":
                    for fund in funds:
                        fund[2] += int(amt)
                elif group == "Class Subtract":
                    for fund in funds:
                        fund[2] -= int(amt)
                else:
                    subject = d[group]
                    students = cur.execute(f"SELECT * from {subject}").fetchall()
                    for fund in funds:
                        if (fund[0], fund[1]) in students:
                            fund[2] -= int(amt)
                
                for fund in funds:
                    cur.execute("UPDATE class_funds SET funds = ? WHERE id = ?", (fund[2], fund[0]))
            funds = [list(fund) for fund in cur.execute("SELECT * from class_funds").fetchall()]

        return render_template("class_funds.html", funds=funds, groups=GROUPS)
    
