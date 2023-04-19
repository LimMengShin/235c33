from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


NAMES = ['Amelia', 'Gillian', 'Louissa', 'Yong Jia', 'Isis', 'Winona', 'Maydalynn', 'Min Jia', 'Nuo Xin', 'Yi Xin', 'Justin', 'Toby', 'Ethan', 'Zhong Yu', 'Kingster', 'Jun Rui', 'Xiang Ling', 'Hua Yu', 'Javier', 'Meng Shin', 'Matthew', 'Cayden', 'Reidon', 'Yun Hao', 'Nicholas', 'Theodore', 'Xander', 'Aaron']
GROUPS = ['h2_physics', 'h2_math', 'h2_econs', 'h2_comp']
funds = {}


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/reset", methods=["GET", "POST"])
def reset():
    with sqlite3.connect("class_funds.db") as con:
        cur = con.cursor()
        #cur.execute("CREATE TABLE class_funds (id INT, name TEXT, funds INT)")
        cur.execute("DELETE FROM class_funds")
        for idx, name in enumerate(NAMES):
            cur.execute("INSERT INTO class_funds (id, name, funds) VALUES (?, ?, ?)", (idx+1, name, 0))
        con.commit()
    return redirect("/funds")


@app.route("/funds", methods=["GET", "POST"])
def funds():
    with sqlite3.connect("class_funds.db") as con:
        cur = con.cursor()
        funds = cur.execute("SELECT * from class_funds").fetchall()
        con.commit()

    if request.method == "GET":
        return render_template("class_funds.html", funds=funds, groups=GROUPS)
            
    elif request.method == "POST":
        group = request.form.get("group")
        amt = request.form.get("amt")
        if not amt.isdigit():
            return
        elif not group:
            return

        return render_template("class_funds.html", funds=funds, groups=GROUPS, amt=amt)
    
