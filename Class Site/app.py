from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

NAMES = ['Amelia', 'Gillian', 'Louissa', 'Yong Jia', 'Isis', 'Winona', 'Maydalynn', 'Min Jia', 'Nuo Xin', 'Yi Xin', 'Justin', 'Toby', 'Ethan', 'Zhong Yu', 'Kingster', 'Jun Rui', 'Xiang Ling', 'Hua Yu', 'Javier', 'Meng Shin', 'Matthew', 'Cayden', 'Reidon', 'Yun Hao', 'Nicholas', 'Theodore', 'Xander', 'Aaron']
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
        funds = cur.execute("SELECT * FROM class_funds").fetchall()
        con.commit()
    return render_template("class_funds.html", funds=funds)

