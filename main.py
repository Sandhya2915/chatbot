from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import sqlite3
import random

app = Flask(__name__)

mybot = ChatBot("PizzaBot",storage_adapter="chatterbot.storage.SQLStorageAdapter")

training_data_quesans = open('training_data/qa.txt').read().splitlines()

training_data = training_data_quesans

trainer = ListTrainer(mybot)
trainer.train(training_data)

pizza=''

db=sqlite3.connect('db1.sqlite3')
cursor = db.cursor()
cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='orders' ''')
if cursor.fetchone()[0]==0 :
    cursor.execute('''CREATE TABLE orders(id INTEGER PRIMARY KEY,name TEXT, phone TEXT, address TEXT,pizza TEXT)''')
db.commit()

flag = 0
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    with sqlite3.connect("db1.sqlite3") as db:
        global flag
        global pizza
        cursor = db.cursor()
        userText = request.args.get('msg')
        if (userText == 'Chicken Dominator' or userText == 'Double Cheese Margarita Pizza' or userText == 'Indi Tandoori Paneer' or userText == 'Chicken Golden Delight'):
            pizza=userText
        if(flag == 1):
            ind = userText.index(';')
            name = userText[:ind]
            temp = userText[ind + 1:]
            ind = temp.index(';')
            phone = temp[:ind]
            address = temp[ind + 1:]
            cursor.execute('''INSERT INTO orders(name, phone, address, pizza) VALUES(?,?,?,?)''',(name, phone, address, pizza))
            cursor.execute('''SELECT id FROM orders WHERE phone=(?)''',(phone,))
            rows=cursor.fetchall()
            db.commit()
            flag = 0
            return 'Your '+pizza+' order has been placed successfully. Your order id is '+str(rows[0][0])
        elif(flag==2):
            myid=int(userText)
            cursor.execute(''' SELECT count(id) FROM orders WHERE id=(?) ''',(myid,))
            if cursor.fetchone()[0] == 0:
                flag=0
                db.commit()
                return 'Kindly make an order with us'
            status = ["Your order is already out for delivery","Your order is being prepared"]
            index = [0,1]
            flag=0
            db.commit()
            return status[random.choice(index)]
        else:
            res = str(mybot.get_response(userText))
            if(res=='Kindly, provide your (name;contact number;delivery address) as in specified format'):
                flag=1
            elif(res=='Please provide your order id'):
                flag=2
            return res

if __name__ == "__main__":
    app.run()

