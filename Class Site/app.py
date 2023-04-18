from flask import Flask, render_template, request
from cs50 import SQL

app = Flask(__name__)

NAMES = ['Amelia', 'Gillian', 'Louissa', 'Yong Jia', 'Isis', 'Winona', 'Maydalynn', 'Min Jia', 'Nuo Xin', 'Yi Xin', 'Justin', 'Toby', 'Ethan', 'Zhong Yu', 'Kingster', 'Jun Rui', 'Xiang Ling', 'Hua Yu', 'Javier', 'Meng Shin', 'Matthew', 'Cayden', 'Reidon', 'Yun Hao', 'Nicholas', 'Theodore', 'Xander', 'Aaron']
funds = {}

db = SQL("sqlite:///class_funds.db")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/reset", methods=["GET", "POST"])
def reset():
    for name in NAMES:
        db.execute("INSERT INTO class_funds (name, funds) VALUES(?, ?)", name, 0)
    funds = db.execute("SELECT * FROM class_funds")
    return render_template("class_funds.html", funds=funds)